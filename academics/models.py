from django.db import models
from django.db.models import Q


class AcademicYear(models.Model):
	school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='academic_years')
	name = models.CharField(max_length=20)
	start_date = models.DateField()
	end_date = models.DateField()
	is_active = models.BooleanField(default=False)

	class Meta:
		db_table = 'academic_years'
		constraints = [
			# Une seule année active par école
			models.UniqueConstraint(
				fields=['school'],
				condition=Q(is_active=True),
				name='unique_active_academic_year_per_school',
			),
			# Nom d'année unique par école (ex: 2025/2026)
			models.UniqueConstraint(
				fields=['school', 'name'],
				name='unique_academic_year_name_per_school',
			),
		]


class Level(models.Model):
	name = models.CharField(max_length=100)
	order = models.PositiveIntegerField()

	class Meta:
		db_table = 'levels'


class SchoolClass(models.Model):
	school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='classes')
	level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='classes')
	academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='classes')
	name = models.CharField(max_length=50)
	capacity = models.PositiveIntegerField(blank=True, null=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		db_table = 'classes'
		constraints = [
			models.UniqueConstraint(
				fields=['school', 'level', 'name', 'academic_year'],
				name='unique_class_per_school_level_name_year',
			)
		]


class Subject(models.Model):
	name = models.CharField(max_length=100)
	is_active = models.BooleanField(default=True)

	class Meta:
		db_table = 'subjects'


class Student(models.Model):
	class Status(models.TextChoices):
		ACTIVE = 'active', 'Active'
		TRANSFERRED = 'transferred', 'Transferred'
		GRADUATED = 'graduated', 'Graduated'

	class Gender(models.TextChoices):
		MALE = 'male', 'Male'
		FEMALE = 'female', 'Female'

	school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='students')
	parent = models.ForeignKey('accounts.ParentProfile', on_delete=models.PROTECT, related_name='students')
	current_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name='students')
	academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='students')
	full_name = models.CharField(max_length=255)
	gender = models.CharField(max_length=10, choices=Gender.choices)
	birth_date = models.DateField()
	registration_number = models.CharField(max_length=100)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'students'
		constraints = [
			models.UniqueConstraint(
				fields=['school', 'registration_number'],
				name='unique_registration_per_school',
			)
		]


class TeachingAssignment(models.Model):
	teacher = models.ForeignKey('accounts.TeacherProfile', on_delete=models.CASCADE, related_name='teaching_assignments')
	school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='teaching_assignments')
	subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teaching_assignments')
	academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='teaching_assignments')

	class Meta:
		db_table = 'teaching_assignments'
		constraints = [
			models.UniqueConstraint(
				fields=['teacher', 'school_class', 'subject', 'academic_year'],
				name='unique_teaching_assignment',
			)
		]


class ClassChangeRequest(models.Model):
	class Status(models.TextChoices):
		PENDING = 'pending', 'Pending'
		APPROVED = 'approved', 'Approved'
		REJECTED = 'rejected', 'Rejected'

	student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='class_change_requests')
	from_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name='class_changes_from')
	to_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name='class_changes_to')
	requested_by = models.ForeignKey('accounts.SecretaryProfile', on_delete=models.PROTECT, related_name='class_change_requests')
	approved_by = models.ForeignKey(
		'accounts.DirectorProfile',
		on_delete=models.PROTECT,
		related_name='approved_class_changes',
		blank=True,
		null=True,
	)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	reason = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	decided_at = models.DateTimeField(blank=True, null=True)

	class Meta:
		db_table = 'class_change_requests'
