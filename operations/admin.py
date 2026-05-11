from django.contrib import admin

from operations.models import Absence, Grade, Incident, SubjectCoefficient


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'academic_year', 'type', 'value', 'entered_by', 'created_at')
    list_filter = ('type', 'academic_year', 'subject')
    search_fields = ('student__full_name', 'student__registration_number')


@admin.register(SubjectCoefficient)
class SubjectCoefficientAdmin(admin.ModelAdmin):
    list_display = ('subject', 'level', 'academic_year', 'coefficient')
    list_filter = ('level', 'academic_year')


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'is_justified', 'recorded_by', 'created_at')
    list_filter = ('is_justified', 'date')
    search_fields = ('student__full_name',)


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'severity', 'date', 'recorded_by', 'created_at')
    list_filter = ('severity', 'date')
    search_fields = ('student__full_name', 'title')
