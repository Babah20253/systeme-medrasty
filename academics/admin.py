from django.contrib import admin

from academics.models import AcademicYear, ClassChangeRequest, Level, SchoolClass, Student, Subject, TeachingAssignment


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'start_date', 'end_date', 'is_active')
    list_filter = ('school', 'is_active')
    search_fields = ('name', 'school__name')


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'level', 'academic_year', 'capacity', 'is_active')
    list_filter = ('school', 'level', 'academic_year', 'is_active')
    search_fields = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'registration_number', 'school', 'current_class', 'status', 'is_active')
    list_filter = ('school', 'status', 'is_active', 'gender')
    search_fields = ('full_name', 'registration_number')


@admin.register(TeachingAssignment)
class TeachingAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'school_class', 'subject', 'academic_year')
    list_filter = ('academic_year',)


@admin.register(ClassChangeRequest)
class ClassChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'from_class', 'to_class', 'status', 'requested_by', 'approved_by', 'created_at')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'decided_at')
