from rest_framework import serializers

from notifications.models import OTPCode, SMSLog
from notifications.services import send_password_reset_otp, verify_password_reset_otp


class OTPCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPCode
        fields = ['id', 'phone', 'code', 'purpose', 'expires_at', 'is_used', 'created_at']
        read_only_fields = ['id', 'expires_at', 'is_used', 'created_at']


class SMSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSLog
        fields = ['id', 'phone', 'message', 'purpose', 'status', 'sent_at', 'failure_reason']


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

    def create(self, validated_data):
        return send_password_reset_otp(validated_data['phone'])


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        if not verify_password_reset_otp(phone=attrs['phone'], code=attrs['code']):
            raise serializers.ValidationError('Invalid or expired OTP.')
        return attrs
