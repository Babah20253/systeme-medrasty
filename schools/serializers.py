from django.db import transaction
from rest_framework import serializers

from accounts.models import DirectorProfile, User
from schools.models import School


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'code', 'address', 'phone', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SchoolCreateWithDirectorSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=50)
    address = serializers.CharField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    director_phone = serializers.CharField(max_length=20)
    director_password = serializers.CharField(write_only=True, min_length=6)

    def validate_code(self, value):
        if School.objects.filter(code=value).exists():
            raise serializers.ValidationError('School code already exists.')
        return value

    def validate_director_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Director phone already exists.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        school = School.objects.create(
            name=validated_data['name'],
            code=validated_data['code'],
            address=validated_data['address'],
            phone=validated_data.get('phone', ''),
        )

        director_user = User.objects.create_user(
            phone=validated_data['director_phone'],
            password=validated_data['director_password'],
            role=User.Role.DIRECTOR,
        )
        DirectorProfile.objects.create(user=director_user, school=school)
        return school
