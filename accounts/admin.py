from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import (
    DirectorProfile,
    ParentProfile,
    SecretaryProfile,
    SuperAdminProfile,
    SupervisorProfile,
    TeacherProfile,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone', 'full_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('phone', 'full_name')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Informations', {'fields': ('full_name', 'role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('phone', 'full_name', 'role', 'password1', 'password2')}),
    )


@admin.register(SuperAdminProfile)
class SuperAdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(DirectorProfile)
class DirectorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')
    list_filter = ('school',)


@admin.register(SecretaryProfile)
class SecretaryProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')
    list_filter = ('school',)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')
    list_filter = ('school',)


@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')
    list_filter = ('school',)


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')
    list_filter = ('school',)
