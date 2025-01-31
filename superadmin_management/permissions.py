from rest_framework.permissions import BasePermission

class IsSuperadmin(BasePermission):
    """Custom permission to allow only Superadmins to access certain views."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "superadmin"