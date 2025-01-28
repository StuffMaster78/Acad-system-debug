from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrSuperAdmin(BasePermission):
    """
    Allows access only to admin or superadmin users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "superadmin"]


class IsSupportOrAdmin(BasePermission):
    """
    Allows access to support staff, admin, or superadmin users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["support", "admin", "superadmin"]


class ReadOnly(BasePermission):
    """
    Allows read-only access for all users.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS