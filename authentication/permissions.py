from rest_framework.permissions import BasePermission

class IsAdminOrSuperAdmin(BasePermission):
    """
    Allow access only to superadmins and admins.
    """
    def has_permission(self, request, view):
        # return request.user.is_authenticated and request.user.role in ["superadmin", "admin"]
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)