from django.db import models


class School(models.Model):
	name = models.CharField(max_length=255)
	code = models.CharField(max_length=50, unique=True)
	address = models.TextField()
	phone = models.CharField(max_length=20, blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'schools'

	def __str__(self):
		return f'{self.name} ({self.code})'
