from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from notifications.serializers import SendOTPSerializer, VerifyOTPSerializer


class OTPViewSet(viewsets.ViewSet):
	permission_classes = [AllowAny]

	@action(detail=False, methods=['post'], url_path='send')
	def send_otp(self, request):
		serializer = SendOTPSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({'detail': 'OTP sent.'}, status=status.HTTP_200_OK)

	@action(detail=False, methods=['post'], url_path='verify')
	def verify_otp(self, request):
		serializer = VerifyOTPSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		return Response({'detail': 'OTP verified.'}, status=status.HTTP_200_OK)
