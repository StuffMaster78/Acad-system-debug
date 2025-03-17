from rest_framework import permissions

class IsAdminSuperadminEditor(permissions.BasePermission):
    """Allows only admins, superadmins, and editors to manage social platforms."""

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.role in ["admin", "superadmin", "editor"]
        return False