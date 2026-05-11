from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models


class UserManager(BaseUserManager):
	def create_user(self, phone, password=None, **extra_fields):
		if not phone:
			raise ValueError('Phone is required.')
		user = self.model(phone=phone, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, phone, password=None, **extra_fields):
		extra_fields.setdefault('role', User.Role.SUPERADMIN)
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('role') != User.Role.SUPERADMIN:
			raise ValueError('Superuser must have role=superadmin.')
		return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	class Role(models.TextChoices):
		SUPERADMIN = 'superadmin', 'Super Admin'
		DIRECTOR = 'director', 'Director'
		SECRETARY = 'secretary', 'Secretary'
		TEACHER = 'teacher', 'Teacher'
		SUPERVISOR = 'supervisor', 'Supervisor'
		PARENT = 'parent', 'Parent'

	phone = models.CharField(max_length=20, unique=True)
	full_name = models.CharField(max_length=255, blank=True)
	role = models.CharField(max_length=20, choices=Role.choices)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = UserManager()

	USERNAME_FIELD = 'phone'
	REQUIRED_FIELDS = []

	class Meta:
		db_table = 'users'

	def __str__(self):
		return f'{self.phone} ({self.role})'

	@property
	def school_id(self):
		if self.role == User.Role.SUPERADMIN:
			return None
		profile_map = {
			User.Role.DIRECTOR: 'director_profile',
			User.Role.SECRETARY: 'secretary_profile',
			User.Role.TEACHER: 'teacher_profile',
			User.Role.SUPERVISOR: 'supervisor_profile',
			User.Role.PARENT: 'parent_profile',
		}
		profile_attr = profile_map.get(self.role)
		profile = getattr(self, profile_attr, None) if profile_attr else None
		return profile.school_id if profile else None


class SuperAdminProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='superadmin_profile')

	class Meta:
		db_table = 'superadmin_profiles'

	def clean(self):
		if SuperAdminProfile.objects.exclude(pk=self.pk).exists():
			raise ValidationError('Only one SuperAdmin profile is allowed in the system.')

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class DirectorProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='director_profile')
	school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='directors')

	class Meta:
		db_table = 'director_profiles'
		constraints = [
			# Un seul directeur actif par école
			models.UniqueConstraint(
				fields=['school'],
				name='unique_director_per_school',
			)
		]


class SecretaryProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='secretary_profile')
	school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='secretaries')

	class Meta:
		db_table = 'secretary_profiles'


class TeacherProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
	school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='teachers')

	class Meta:
		db_table = 'teacher_profiles'


class SupervisorProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')
	school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='supervisors')

	class Meta:
		db_table = 'supervisor_profiles'


class ParentProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
	school = models.ForeignKey('schools.School', on_delete=models.CASCADE, related_name='parents')

	class Meta:
		db_table = 'parent_profiles'
