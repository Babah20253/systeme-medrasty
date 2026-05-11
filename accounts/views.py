from django.db.models import Q
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import User
from accounts.serializers import (
	LoginSerializer,
	PasswordResetConfirmSerializer,
	PasswordResetRequestSerializer,
	UserCreateSerializer,
	UserSerializer,
)
from notifications.services import send_password_reset_otp, verify_password_reset_otp


class LoginView(TokenObtainPairView):
	serializer_class = LoginSerializer
	permission_classes = [AllowAny]


def _filter_users_by_school(queryset, school_id):
	return queryset.filter(
		Q(director_profile__school_id=school_id)
		| Q(secretary_profile__school_id=school_id)
		| Q(teacher_profile__school_id=school_id)
		| Q(supervisor_profile__school_id=school_id)
		| Q(parent_profile__school_id=school_id)
	).distinct()


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		qs = User.objects.all().order_by('-created_at')
		user = self.request.user
		if user.role == User.Role.SUPERADMIN:
			return qs
		if user.school_id is None:
			return User.objects.none()
		return _filter_users_by_school(qs, user.school_id)

	def get_serializer_class(self):
		if self.action == 'create':
			return UserCreateSerializer
		return UserSerializer

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=['post'], url_path='deactivate')
	def deactivate(self, request, pk=None):
		"""Désactiver un utilisateur (superadmin ou directeur de la même école)."""
		target = self.get_object()
		if request.user.role == User.Role.SUPERADMIN:
			pass  # autorisé
		elif request.user.role == User.Role.DIRECTOR:
			if target.school_id != request.user.school_id:
				return Response({'detail': 'Vous ne pouvez pas désactiver un utilisateur d\'une autre école.'}, status=status.HTTP_403_FORBIDDEN)
		else:
			return Response({'detail': 'Permission insuffisante.'}, status=status.HTTP_403_FORBIDDEN)

		if not target.is_active:
			return Response({'detail': 'Cet utilisateur est déjà inactif.'}, status=status.HTTP_400_BAD_REQUEST)

		target.is_active = False
		target.save(update_fields=['is_active'])
		return Response({'detail': f'Utilisateur {target.phone} désactivé avec succès.'}, status=status.HTTP_200_OK)


class PasswordResetViewSet(viewsets.ViewSet):
	permission_classes = [AllowAny]

	@action(detail=False, methods=['post'], url_path='request')
	def request_reset(self, request):
		serializer = PasswordResetRequestSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		phone = serializer.validated_data['phone']

		if not User.objects.filter(phone=phone, is_active=True).exists():
			return Response({'detail': 'If this phone exists, an OTP has been sent.'}, status=status.HTTP_200_OK)

		send_password_reset_otp(phone)
		return Response({'detail': 'OTP sent.'}, status=status.HTTP_200_OK)

	@action(detail=False, methods=['post'], url_path='confirm')
	def confirm_reset(self, request):
		serializer = PasswordResetConfirmSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		phone = serializer.validated_data['phone']
		code = serializer.validated_data['code']
		new_password = serializer.validated_data['new_password']

		if not verify_password_reset_otp(phone=phone, code=code):
			return Response({'detail': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			user = User.objects.get(phone=phone, is_active=True)
		except User.DoesNotExist:
			return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

		user.set_password(new_password)
		user.save(update_fields=['password'])
		return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)
