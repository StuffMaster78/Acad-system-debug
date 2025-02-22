from rest_framework.permissions import BasePermission
from superadmin_management.models import SuperadminProfile, Blacklist

class IsSuperadmin(BasePermission):
    """Custom permission to allow only Superadmins with an active profile."""

    def has_permission(self, request, view):
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            return False

        # Ensure user has a Superadmin profile
        if not hasattr(request.user, 'superadmin_profile'):
            return False

        # Check if the user is blacklisted
        if Blacklist.objects.filter(user=request.user, is_active=True).exists():
            return False

        return True  # User is a valid Superadmin
    

class IsSuperadminOrAdmin(BasePermission):
    """Allows access to Superadmins & Admins, but limits some actions."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["superadmin", "admin"]

class IsSuperadminOnly(BasePermission):
    """Only allows Superadmins full control."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "superadmin"