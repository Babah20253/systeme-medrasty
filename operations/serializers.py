from rest_framework import serializers

from operations.models import Absence, Grade, Incident, SubjectCoefficient


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'student', 'subject', 'academic_year', 'type', 'value', 'entered_by', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        request = self.context['request']
        student = attrs.get('student') or getattr(self.instance, 'student', None)
        subject = attrs.get('subject') or getattr(self.instance, 'subject', None)
        academic_year = attrs.get('academic_year') or getattr(self.instance, 'academic_year', None)
        entered_by = attrs.get('entered_by') or getattr(self.instance, 'entered_by', None)

        if request.user.role == 'teacher':
            if not hasattr(request.user, 'teacher_profile'):
                raise serializers.ValidationError('Teacher profile not found.')
            attrs['entered_by'] = request.user.teacher_profile
            entered_by = attrs['entered_by']

        if not student or not subject or not academic_year or not entered_by:
            return attrs

        class_obj = student.current_class
        # Vérification: l'étudiant appartient à l'année académique donnée
        if student.academic_year_id != academic_year.id:
            raise serializers.ValidationError(
                'La note doit correspondre à l’année scolaire de l’étudiant.'
            )
        if entered_by.school_id != student.school_id:
            raise serializers.ValidationError('Teacher and student must be in the same school.')
        if request.user.role != 'superadmin' and student.school_id != request.user.school_id:
            raise serializers.ValidationError('Cross-school grade entry is not allowed.')
        if class_obj.academic_year_id != academic_year.id:
            raise serializers.ValidationError('Student class academic year does not match grade academic year.')

        assignment_exists = entered_by.teaching_assignments.filter(
            school_class=class_obj,
            subject=subject,
            academic_year=academic_year,
        ).exists()
        if not assignment_exists:
            raise serializers.ValidationError('Teacher is not assigned to this class/subject.')

        return attrs


class SubjectCoefficientSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectCoefficient
        fields = ['id', 'subject', 'level', 'academic_year', 'coefficient']


class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absence
        fields = ['id', 'student', 'date', 'recorded_by', 'is_justified', 'proof_document', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        request = self.context['request']
        student = attrs.get('student') or getattr(self.instance, 'student', None)
        recorded_by = attrs.get('recorded_by') or getattr(self.instance, 'recorded_by', None)

        if request.user.role == 'supervisor':
            if not hasattr(request.user, 'supervisor_profile'):
                raise serializers.ValidationError('Supervisor profile not found.')
            attrs['recorded_by'] = request.user.supervisor_profile
            recorded_by = attrs['recorded_by']

        if student and request.user.role != 'superadmin' and student.school_id != request.user.school_id:
            raise serializers.ValidationError('Cross-school absence entry is not allowed.')

        if student and recorded_by and student.school_id != recorded_by.school_id:
            raise serializers.ValidationError('Supervisor and student must belong to the same school.')

        return attrs


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['id', 'student', 'recorded_by', 'title', 'description', 'severity', 'date', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        request = self.context['request']
        student = attrs.get('student') or getattr(self.instance, 'student', None)
        recorded_by = attrs.get('recorded_by') or getattr(self.instance, 'recorded_by', None)

        if request.user.role == 'supervisor':
            if not hasattr(request.user, 'supervisor_profile'):
                raise serializers.ValidationError('Supervisor profile not found.')
            attrs['recorded_by'] = request.user.supervisor_profile
            recorded_by = attrs['recorded_by']

        if student and request.user.role != 'superadmin' and student.school_id != request.user.school_id:
            raise serializers.ValidationError('Cross-school incident entry is not allowed.')

        if student and recorded_by and student.school_id != recorded_by.school_id:
            raise serializers.ValidationError('Supervisor and student must belong to the same school.')

        return attrs
