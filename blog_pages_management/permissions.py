from rest_framework import permissions

class IsAdminSuperadminEditor(permissions.BasePermission):
    """Allows only admins, superadmins, and editors to manage social platforms."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Ensure superusers always have access
        if request.user.is_superuser:
            return True

        # Securely check role existence
        user_role = getattr(request.user, "role", None)
        return user_role in {"admin", "superadmin", "editor"}