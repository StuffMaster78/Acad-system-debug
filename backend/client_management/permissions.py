from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrSuperAdmin(BasePermission):
    """
    Custom permission to allow only admins and superadmins to access certain views.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "superadmin"]

class IsClient(BasePermission):
    """
    Custom permission to allow only clients to access their own data.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "client"

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to allow admins to edit but everyone can view (read-only access).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # Read-only methods
            return True
        return request.user.is_authenticated and request.user.role in ["admin", "superadmin"]

class IsSelfOrAdmin(BasePermission):
    """
    Custom permission to allow clients to access their own profiles,
    and admins to access any client's profile.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.role in ["admin", "superadmin"] or obj.user == request.user
        return False
