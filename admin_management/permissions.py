from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Custom permission to allow only Admins to access certain views."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"