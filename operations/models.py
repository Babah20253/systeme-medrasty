from django.db import models


class Grade(models.Model):
	class GradeType(models.TextChoices):
		TEST = 'test', 'Test'
		EXAM = 'exam', 'Exam'

	student = models.ForeignKey('academics.Student', on_delete=models.CASCADE, related_name='grades')
	subject = models.ForeignKey('academics.Subject', on_delete=models.PROTECT, related_name='grades')
	academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.PROTECT, related_name='grades')
	type = models.CharField(max_length=10, choices=GradeType.choices)
	value = models.DecimalField(max_digits=5, decimal_places=2)
	entered_by = models.ForeignKey('accounts.TeacherProfile', on_delete=models.PROTECT, related_name='entered_grades')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'grades'
		constraints = [
			models.UniqueConstraint(
				fields=['student', 'subject', 'academic_year', 'type'],
				name='unique_grade_type_per_student_subject_year',
			)
		]


class SubjectCoefficient(models.Model):
	subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='coefficients')
	level = models.ForeignKey('academics.Level', on_delete=models.CASCADE, related_name='subject_coefficients')
	academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE, related_name='subject_coefficients', null=True, blank=True)
	coefficient = models.DecimalField(max_digits=5, decimal_places=2)

	class Meta:
		db_table = 'subject_coefficients'
		constraints = [
			models.UniqueConstraint(
				fields=['subject', 'level', 'academic_year'],
				name='unique_subject_coefficient_per_level_year',
			)
		]


class Absence(models.Model):
	student = models.ForeignKey('academics.Student', on_delete=models.CASCADE, related_name='absences')
	date = models.DateField()
	recorded_by = models.ForeignKey('accounts.SupervisorProfile', on_delete=models.PROTECT, related_name='recorded_absences')
	is_justified = models.BooleanField(default=False)
	proof_document = models.FileField(upload_to='absences/proofs/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'absences'
		constraints = [
			models.UniqueConstraint(
				fields=['student', 'date'],
				name='unique_absence_per_student_per_day',
			)
		]


class Incident(models.Model):
	class Severity(models.TextChoices):
		LOW = 'low', 'Low'
		MEDIUM = 'medium', 'Medium'
		HIGH = 'high', 'High'

	student = models.ForeignKey('academics.Student', on_delete=models.CASCADE, related_name='incidents')
	recorded_by = models.ForeignKey('accounts.SupervisorProfile', on_delete=models.PROTECT, related_name='recorded_incidents')
	title = models.CharField(max_length=255)
	description = models.TextField()
	severity = models.CharField(max_length=10, choices=Severity.choices)
	date = models.DateField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'incidents'
