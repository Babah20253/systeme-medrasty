from rest_framework.permissions import BasePermission

from accounts.models import User


class _RolePermission(BasePermission):
    allowed_role = None

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and self.allowed_role is not None
            and user.role == self.allowed_role
        )


class IsSuperAdmin(_RolePermission):
    allowed_role = User.Role.SUPERADMIN


class IsDirector(_RolePermission):
    allowed_role = User.Role.DIRECTOR


class IsSecretary(_RolePermission):
    allowed_role = User.Role.SECRETARY


class IsTeacher(_RolePermission):
    allowed_role = User.Role.TEACHER


class IsSupervisor(_RolePermission):
    allowed_role = User.Role.SUPERVISOR


class IsParent(_RolePermission):
    allowed_role = User.Role.PARENT
