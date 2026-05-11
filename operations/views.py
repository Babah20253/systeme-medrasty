from decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from operations.models import Absence, Grade, Incident, SubjectCoefficient
from operations.serializers import AbsenceSerializer, GradeSerializer, IncidentSerializer, SubjectCoefficientSerializer


class GradeViewSet(viewsets.ModelViewSet):
	serializer_class = GradeSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		qs = Grade.objects.select_related('student', 'subject', 'academic_year', 'entered_by').all().order_by('-created_at')
		if user.role == User.Role.SUPERADMIN:
			return qs
		if user.role == User.Role.PARENT:
			return qs.filter(student__parent__user=user)
		if user.school_id is None:
			return Grade.objects.none()
		if user.role == User.Role.TEACHER:
			return qs.filter(entered_by__user=user)
		return qs.filter(student__school_id=user.school_id)

	def create(self, request, *args, **kwargs):
		if request.user.role not in {User.Role.TEACHER, User.Role.SUPERADMIN}:
			return Response({'detail': 'Only teacher or superadmin can add grade.'}, status=status.HTTP_403_FORBIDDEN)
		return super().create(request, *args, **kwargs)

	@action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
	def list_student_grades(self, request, student_id=None):
		queryset = self.get_queryset().filter(student_id=student_id)
		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)/average')
	def student_average(self, request, student_id=None):
		"""
		Calcule dynamiquement la moyenne générale d'un étudiant.
		Moyenne par matière = moyenne(tests) + exam (non stockée en DB).
		Moyenne générale = Σ(moy_matière × coef) / Σ(coef).
		"""
		from academics.models import Student
		from operations.models import SubjectCoefficient

		# Récupérer l'étudiant et vérifier accès
		try:
			student = Student.objects.select_related('current_class__level').get(pk=student_id)
		except Student.DoesNotExist:
			return Response({'detail': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

		if request.user.role not in {User.Role.SUPERADMIN} and student.school_id != request.user.school_id:
			if request.user.role == User.Role.PARENT and not student.parent.user == request.user:
				return Response({'detail': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)

		grades = self.get_queryset().filter(student=student)
		level = student.current_class.level

		# Regrouper les notes par matière
		subject_grades = {}
		for g in grades:
			sid = g.subject_id
			if sid not in subject_grades:
				subject_grades[sid] = {'tests': [], 'exam': None, 'subject': g.subject}
			if g.type == Grade.GradeType.TEST:
				subject_grades[sid]['tests'].append(g.value)
			elif g.type == Grade.GradeType.EXAM:
				subject_grades[sid]['exam'] = g.value

		coefficients = {
			c.subject_id: c.coefficient
			for c in SubjectCoefficient.objects.filter(level=level, academic_year=student.academic_year)
		}

		details = []
		total_weighted = Decimal('0')
		total_coef = Decimal('0')

		for sid, data in subject_grades.items():
			tests = data['tests']
			exam = data['exam']

			# Formule correcte: (somme_tests + note_exam) / (nb_tests + 1)
			if tests and exam is not None:
				subject_avg = (sum(tests) + exam) / (len(tests) + 1)
			elif tests:
				subject_avg = sum(tests) / len(tests)
			elif exam is not None:
				subject_avg = exam
			else:
				continue  # Pas assez de notes, ignorer la matière

			# Coefficient obligatoire: lever une erreur si absent
			if sid not in coefficients:
				return Response(
					{'detail': f'Coefficient manquant pour la matière id={sid} au niveau "{level.name}". Définir le coefficient avant de calculer la moyenne.'},
					status=status.HTTP_400_BAD_REQUEST,
				)
			coef = coefficients[sid]
			total_weighted += subject_avg * coef
			total_coef += coef
			tests_avg_display = round(float(sum(tests) / len(tests)), 2) if tests else None
			details.append({
				'subject_id': sid,
				'subject_name': data['subject'].name,
				'test_average': tests_avg_display,
				'exam': round(float(exam), 2) if exam is not None else None,
				'subject_average': round(float(subject_avg), 2),
				'coefficient': float(coef),
			})

		general_average = round(float(total_weighted / total_coef), 2) if total_coef else None

		return Response({
			'student_id': student.id,
			'student_name': student.full_name,
			'level': level.name,
			'general_average': general_average,
			'details': details,
		}, status=status.HTTP_200_OK)


# ─── SubjectCoefficient ──────────────────────────────────────────────────────

class SubjectCoefficientViewSet(viewsets.ModelViewSet):
	serializer_class = SubjectCoefficientSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return SubjectCoefficient.objects.select_related('subject', 'level').all().order_by('level__order', 'subject__name')

	def perform_create(self, serializer):
		if self.request.user.role not in {User.Role.SUPERADMIN}:
			raise PermissionDenied('Only superadmin can manage subject coefficients.')
		serializer.save()

	def perform_update(self, serializer):
		if self.request.user.role not in {User.Role.SUPERADMIN}:
			raise PermissionDenied('Only superadmin can manage subject coefficients.')
		serializer.save()

	def perform_destroy(self, instance):
		if self.request.user.role not in {User.Role.SUPERADMIN}:
			raise PermissionDenied('Only superadmin can manage subject coefficients.')
		instance.delete()


class AbsenceViewSet(viewsets.ModelViewSet):
	serializer_class = AbsenceSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		qs = Absence.objects.select_related('student', 'recorded_by').all().order_by('-date')
		if user.role == User.Role.SUPERADMIN:
			return qs
		if user.role == User.Role.PARENT:
			return qs.filter(student__parent__user=user)
		if user.school_id is None:
			return Absence.objects.none()
		if user.role == User.Role.SUPERVISOR:
			return qs.filter(recorded_by__user=user)
		return qs.filter(student__school_id=user.school_id)

	def create(self, request, *args, **kwargs):
		if request.user.role not in {User.Role.SUPERVISOR, User.Role.SUPERADMIN}:
			return Response({'detail': 'Only supervisor or superadmin can add absence.'}, status=status.HTTP_403_FORBIDDEN)
		return super().create(request, *args, **kwargs)


class IncidentViewSet(viewsets.ModelViewSet):
	serializer_class = IncidentSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		qs = Incident.objects.select_related('student', 'recorded_by').all().order_by('-date')
		if user.role == User.Role.SUPERADMIN:
			return qs
		if user.role == User.Role.PARENT:
			return qs.filter(student__parent__user=user)
		if user.school_id is None:
			return Incident.objects.none()
		if user.role == User.Role.SUPERVISOR:
			return qs.filter(recorded_by__user=user)
		return qs.filter(student__school_id=user.school_id)

	def create(self, request, *args, **kwargs):
		if request.user.role not in {User.Role.SUPERVISOR, User.Role.SUPERADMIN}:
			return Response({'detail': 'Only supervisor or superadmin can add incident.'}, status=status.HTTP_403_FORBIDDEN)
		return super().create(request, *args, **kwargs)
