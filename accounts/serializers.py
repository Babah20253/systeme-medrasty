from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import (
    DirectorProfile,
    ParentProfile,
    SecretaryProfile,
    SupervisorProfile,
    TeacherProfile,
    User,
)
from schools.models import School


class LoginSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['school_id'] = self.user.school_id
        return data


class UserSerializer(serializers.ModelSerializer):
    school_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'phone',
            'role',
            'is_active',
            'school_id',
            'created_at',
            'updated_at',
        ]

    def get_school_id(self, obj):
        return obj.school_id


class UserCreateSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=User.Role.choices)
    school_id = serializers.IntegerField(required=False)

    def validate(self, attrs):
        request = self.context['request']
        creator = request.user
        role = attrs['role']

        allowed_map = {
            User.Role.SUPERADMIN: {User.Role.DIRECTOR},
            User.Role.DIRECTOR: {User.Role.SECRETARY},
            User.Role.SECRETARY: {User.Role.TEACHER, User.Role.SUPERVISOR, User.Role.PARENT},
        }
        allowed = allowed_map.get(creator.role, set())
        if role not in allowed:
            raise serializers.ValidationError('You cannot create this role.')

        if User.objects.filter(phone=attrs['phone']).exists():
            raise serializers.ValidationError({'phone': 'Phone already exists.'})

        if creator.role == User.Role.SUPERADMIN:
            school_id = attrs.get('school_id')
            if not school_id:
                raise serializers.ValidationError({'school_id': 'school_id is required for director creation.'})
            try:
                attrs['school'] = School.objects.get(id=school_id)
            except School.DoesNotExist as exc:
                raise serializers.ValidationError({'school_id': 'School not found.'}) from exc
        else:
            if creator.school_id is None:
                raise serializers.ValidationError('Creator is not linked to a school.')
            attrs['school'] = School.objects.get(id=creator.school_id)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data['role']
        school = validated_data['school']
        user = User.objects.create_user(
            phone=validated_data['phone'],
            password=validated_data['password'],
            role=role,
        )

        if role == User.Role.DIRECTOR:
            DirectorProfile.objects.create(user=user, school=school)
        elif role == User.Role.SECRETARY:
            SecretaryProfile.objects.create(user=user, school=school)
        elif role == User.Role.TEACHER:
            TeacherProfile.objects.create(user=user, school=school)
        elif role == User.Role.SUPERVISOR:
            SupervisorProfile.objects.create(user=user, school=school)
        elif role == User.Role.PARENT:
            ParentProfile.objects.create(user=user, school=school)

        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)


class PasswordResetConfirmSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)
