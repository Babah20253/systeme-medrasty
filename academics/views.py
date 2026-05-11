from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from academics.models import AcademicYear, ClassChangeRequest, Level, SchoolClass, Student, Subject, TeachingAssignment
from academics.serializers import (
    AcademicYearSerializer,
    ClassChangeRequestSerializer,
    ClassSerializer,
    LevelSerializer,
    StudentSerializer,
    SubjectSerializer,
    TeachingAssignmentSerializer,
)
from accounts.models import User


def _is_in_roles(user, *roles):
	return user.role in set(roles)


# ─── AcademicYear ───────────────────────────────────────────────────────────

class AcademicYearViewSet(viewsets.ModelViewSet):
	serializer_class = AcademicYearSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		qs = AcademicYear.objects.select_related('school').all().order_by('-name')
		if user.role == User.Role.SUPERADMIN:
			return qs
		if user.school_id is None:
			return AcademicYear.objects.none()
		return qs.filter(school_id=user.school_id)

	def perform_create(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can manage academic years.')
		serializer.save()

	def perform_update(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can manage academic years.')
		serializer.save()

	def perform_destroy(self, instance):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can manage academic years.')
		instance.delete()


# ─── Level ──────────────────────────────────────────────────────────────────

class LevelViewSet(viewsets.ModelViewSet):
	serializer_class = LevelSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return Level.objects.all().order_by('order')

	def perform_create(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN):
			raise PermissionDenied('Only superadmin can manage levels.')
		serializer.save()

	def perform_update(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN):
			raise PermissionDenied('Only superadmin can manage levels.')
		serializer.save()

	def perform_destroy(self, instance):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN):
			raise PermissionDenied('Only superadmin can manage levels.')
		instance.delete()


# ─── Subject ─────────────────────────────────────────────────────────────────

class SubjectViewSet(viewsets.ModelViewSet):
	serializer_class = SubjectSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		return Subject.objects.all().order_by('name')

	def perform_create(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN):
			raise PermissionDenied('Only superadmin can manage subjects.')
		serializer.save()

	def perform_update(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN):
			raise PermissionDenied('Only superadmin can manage subjects.')
		serializer.save()

	def perform_destroy(self, instance):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN):
			raise PermissionDenied('Only superadmin can manage subjects.')
		instance.delete()


# ─── ClassChangeRequest ──────────────────────────────────────────────────────

class ClassChangeRequestViewSet(viewsets.ModelViewSet):
	serializer_class = ClassChangeRequestSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		qs = ClassChangeRequest.objects.select_related(
			'student', 'from_class', 'to_class', 'requested_by', 'approved_by'
		).all().order_by('-created_at')
		if user.role == User.Role.SUPERADMIN:
			return qs
		if user.school_id is None:
			return ClassChangeRequest.objects.none()
		return qs.filter(student__school_id=user.school_id)

	def perform_create(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SECRETARY, User.Role.SUPERADMIN):
			raise PermissionDenied('Only secretary or superadmin can request class changes.')
		# Automatically set requested_by to current secretary
		if self.request.user.role == User.Role.SECRETARY:
			serializer.save(requested_by=self.request.user.secretary_profile)
		else:
			serializer.save()

	@action(detail=True, methods=['post'], url_path='approve')
	def approve(self, request, pk=None):
		if not _is_in_roles(request.user, User.Role.DIRECTOR, User.Role.SUPERADMIN):
			return Response({'detail': 'Only director can approve class changes.'}, status=status.HTTP_403_FORBIDDEN)

		change_request = self.get_object()
		if change_request.status != ClassChangeRequest.Status.PENDING:
			return Response({'detail': 'Only pending requests can be approved.'}, status=status.HTTP_400_BAD_REQUEST)

		# Validate both classes belong to same school as user
		if request.user.role == User.Role.DIRECTOR and change_request.student.school_id != request.user.school_id:
			return Response({'detail': 'Cross-school approval is not allowed.'}, status=status.HTTP_403_FORBIDDEN)

		change_request.status = ClassChangeRequest.Status.APPROVED
		change_request.decided_at = timezone.now()
		if request.user.role == User.Role.DIRECTOR:
			change_request.approved_by = request.user.director_profile
		change_request.save()

		# Move student to new class
		change_request.student.current_class = change_request.to_class
		change_request.student.save(update_fields=['current_class'])

		return Response(ClassChangeRequestSerializer(change_request).data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['post'], url_path='reject')
	def reject(self, request, pk=None):
		if not _is_in_roles(request.user, User.Role.DIRECTOR, User.Role.SUPERADMIN):
			return Response({'detail': 'Only director can reject class changes.'}, status=status.HTTP_403_FORBIDDEN)

		change_request = self.get_object()
		if change_request.status != ClassChangeRequest.Status.PENDING:
			return Response({'detail': 'Only pending requests can be rejected.'}, status=status.HTTP_400_BAD_REQUEST)

		if request.user.role == User.Role.DIRECTOR and change_request.student.school_id != request.user.school_id:
			return Response({'detail': 'Cross-school rejection is not allowed.'}, status=status.HTTP_403_FORBIDDEN)

		change_request.status = ClassChangeRequest.Status.REJECTED
		change_request.decided_at = timezone.now()
		if request.user.role == User.Role.DIRECTOR:
			change_request.approved_by = request.user.director_profile
		change_request.save()

		return Response(ClassChangeRequestSerializer(change_request).data, status=status.HTTP_200_OK)


class ClassViewSet(viewsets.ModelViewSet):
	serializer_class = ClassSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		qs = SchoolClass.objects.select_related('school', 'level', 'academic_year').all().order_by('name')
		if user.role == User.Role.SUPERADMIN:
			return qs
		if user.school_id is None:
			return SchoolClass.objects.none()
		if user.role == User.Role.TEACHER:
			return qs.filter(teaching_assignments__teacher__user=user).distinct()
		return qs.filter(school_id=user.school_id)

	def perform_create(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can create classes.')
		serializer.save()

	def perform_update(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can update classes.')
		serializer.save()

	def perform_destroy(self, instance):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can delete classes.')
		instance.delete()


class StudentViewSet(viewsets.ModelViewSet):
	serializer_class = StudentSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		qs = Student.objects.select_related('school', 'parent', 'current_class', 'academic_year').all().order_by('-created_at')
		if user.role == User.Role.SUPERADMIN:
			return qs
		if user.role == User.Role.PARENT:
			return qs.filter(parent__user=user)
		if user.school_id is None:
			return Student.objects.none()
		return qs.filter(school_id=user.school_id)

	def perform_create(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can create students.')
		serializer.save()

	def perform_update(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can update students.')
		serializer.save()

	def perform_destroy(self, instance):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can delete students.')
		instance.delete()


class TeachingAssignmentViewSet(viewsets.ModelViewSet):
	serializer_class = TeachingAssignmentSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		qs = TeachingAssignment.objects.select_related('teacher', 'school_class', 'subject', 'academic_year').all()
		if user.role == User.Role.SUPERADMIN:
			return qs
		if user.role == User.Role.TEACHER:
			return qs.filter(teacher__user=user)
		if user.school_id is None:
			return TeachingAssignment.objects.none()
		return qs.filter(school_class__school_id=user.school_id)

	def perform_create(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can assign teachers.')
		serializer.save()

	def perform_update(self, serializer):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can update assignments.')
		serializer.save()

	def perform_destroy(self, instance):
		if not _is_in_roles(self.request.user, User.Role.SUPERADMIN, User.Role.DIRECTOR, User.Role.SECRETARY):
			raise PermissionDenied('Only superadmin/director/secretary can delete assignments.')
		instance.delete()
