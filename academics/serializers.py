from rest_framework import serializers

from academics.models import (
    AcademicYear,
    ClassChangeRequest,
    Level,
    SchoolClass,
    Student,
    Subject,
    TeachingAssignment,
)


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'school', 'name', 'start_date', 'end_date', 'is_active']


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name', 'order']


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = ['id', 'school', 'level', 'academic_year', 'name', 'capacity', 'is_active']

    def validate(self, attrs):
        request = self.context['request']
        school = attrs.get('school') or getattr(self.instance, 'school', None)
        academic_year = attrs.get('academic_year') or getattr(self.instance, 'academic_year', None)

        if request.user.role != 'superadmin' and school and school.id != request.user.school_id:
            raise serializers.ValidationError('Cross-school class creation is not allowed.')

        if school and academic_year and academic_year.school_id != school.id:
            raise serializers.ValidationError('academic_year must belong to the same school.')
        return attrs


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'is_active']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'school',
            'parent',
            'current_class',
            'academic_year',
            'full_name',
            'gender',
            'birth_date',
            'registration_number',
            'status',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        request = self.context['request']
        school = attrs.get('school') or getattr(self.instance, 'school', None)
        parent = attrs.get('parent') or getattr(self.instance, 'parent', None)
        current_class = attrs.get('current_class') or getattr(self.instance, 'current_class', None)
        academic_year = attrs.get('academic_year') or getattr(self.instance, 'academic_year', None)

        if request.user.role != 'superadmin' and school and school.id != request.user.school_id:
            raise serializers.ValidationError('Cross-school student write is not allowed.')

        if parent and school and parent.school_id != school.id:
            raise serializers.ValidationError('Parent must belong to the same school.')

        if current_class and school and current_class.school_id != school.id:
            raise serializers.ValidationError('Class must belong to the same school.')

        if academic_year and school and academic_year.school_id != school.id:
            raise serializers.ValidationError('Academic year must belong to the same school.')

        return attrs


class TeachingAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeachingAssignment
        fields = ['id', 'teacher', 'school_class', 'subject', 'academic_year']

    def validate(self, attrs):
        request = self.context['request']
        teacher = attrs.get('teacher') or getattr(self.instance, 'teacher', None)
        school_class = attrs.get('school_class') or getattr(self.instance, 'school_class', None)
        academic_year = attrs.get('academic_year') or getattr(self.instance, 'academic_year', None)

        if not teacher or not school_class or not academic_year:
            return attrs

        class_school_id = school_class.school_id
        if request.user.role != 'superadmin' and class_school_id != request.user.school_id:
            raise serializers.ValidationError('Cross-school assignment is not allowed.')

        if teacher.school_id != class_school_id:
            raise serializers.ValidationError('Teacher must belong to the same school as class.')

        if academic_year.school_id != class_school_id:
            raise serializers.ValidationError('Academic year must belong to the same school as class.')

        return attrs


class ClassChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassChangeRequest
        fields = [
            'id',
            'student',
            'from_class',
            'to_class',
            'requested_by',
            'approved_by',
            'status',
            'reason',
            'created_at',
            'decided_at',
        ]
        read_only_fields = ['id', 'approved_by', 'status', 'decided_at', 'created_at']

    def validate(self, attrs):
        student = attrs.get('student')
        from_class = attrs.get('from_class')
        to_class = attrs.get('to_class')

        if student and from_class:
            if student.current_class_id != from_class.id:
                raise serializers.ValidationError(
                    {'from_class': "La classe 'from_class' ne correspond pas à la classe actuelle de l'étudiant."}
                )
        if from_class and to_class and from_class.id == to_class.id:
            raise serializers.ValidationError(
                {'to_class': "La classe de destination doit être différente de la classe actuelle."}
            )
        if student and to_class:
            if student.school_id != to_class.school_id:
                raise serializers.ValidationError(
                    {'to_class': "La classe de destination doit appartenir à la même école que l'étudiant."}
                )
        return attrs
