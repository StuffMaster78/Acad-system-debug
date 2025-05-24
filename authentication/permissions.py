from rest_framework.permissions import BasePermission

class IsAdminOrSuperAdmin(BasePermission):
    """
    Allow access only to superadmins and admins.
    """
    def has_permission(self, request, view):
        # return request.user.is_authenticated and request.user.role in ["superadmin", "admin"]
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
    
class IsSuperadmin(BasePermission):
    """Allows access only to Superadmin users."""

    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "superadmin"


class IsAdmin(BasePermission):
    """Allows access only to Admin users."""

    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "admin"


class IsSupport(BasePermission):
    """Allows access only to Support users."""

    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "support"


class IsClient(BasePermission):
    """Allows access only to Client users."""

    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "client"


class IsWriter(BasePermission):
    """Allows access only to Writer users."""

    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "writer"


class IsEditor(BasePermission):
    """Allows access only to Editor users."""

    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role == "editor"
    

class IsInRole(BasePermission):
    """
    Allows access if the user's role is in the allowed roles.
    Usage:
        permission_classes = [IsInRole(('admin', 'superadmin'))]
    """

    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request, view):
        return hasattr(request.user, "role") and request.user.role in self.allowed_roles
