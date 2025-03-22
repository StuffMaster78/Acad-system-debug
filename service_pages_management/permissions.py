from rest_framework import permissions


class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Custom permission to allow only admins or superadmins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser
        )
