from datetime import timedelta
from random import randint

from django.utils import timezone

from notifications.models import OTPCode, SMSLog


def _generate_code():
    return f'{randint(100000, 999999)}'


def send_password_reset_otp(phone):
    code = _generate_code()
    expires_at = timezone.now() + timedelta(minutes=5)

    otp = OTPCode.objects.create(
        phone=phone,
        code=code,
        purpose=OTPCode.Purpose.PASSWORD_RESET,
        expires_at=expires_at,
    )

    SMSLog.objects.create(
        phone=phone,
        message=f'Your MEDRASTY OTP code is: {code}',
        purpose=SMSLog.Purpose.OTP,
        status=SMSLog.Status.SENT,
        sent_at=timezone.now(),
    )
    return otp


def verify_password_reset_otp(phone, code):
    otp = (
        OTPCode.objects.filter(
            phone=phone,
            code=code,
            purpose=OTPCode.Purpose.PASSWORD_RESET,
            is_used=False,
            expires_at__gt=timezone.now(),
        )
        .order_by('-created_at')
        .first()
    )
    if not otp:
        return False

    otp.is_used = True
    otp.save(update_fields=['is_used'])
    return True
