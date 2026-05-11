from django.db import models


class OTPCode(models.Model):
	class Purpose(models.TextChoices):
		PASSWORD_RESET = 'password_reset', 'Password Reset'

	phone = models.CharField(max_length=20)
	code = models.CharField(max_length=6)
	purpose = models.CharField(max_length=30, choices=Purpose.choices)
	expires_at = models.DateTimeField()
	is_used = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'otp_codes'


class SMSLog(models.Model):
	class Purpose(models.TextChoices):
		OTP = 'otp', 'OTP'

	class Status(models.TextChoices):
		PENDING = 'pending', 'Pending'
		SENT = 'sent', 'Sent'
		FAILED = 'failed', 'Failed'

	phone = models.CharField(max_length=20)
	message = models.TextField()
	purpose = models.CharField(max_length=20, choices=Purpose.choices)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	sent_at = models.DateTimeField(blank=True, null=True)
	failure_reason = models.TextField(blank=True)

	class Meta:
		db_table = 'sms_logs'
