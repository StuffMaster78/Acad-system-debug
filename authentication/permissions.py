from rest_framework.permissions import BasePermission
from authentication.constants import ROLE_HIERARCHY


class IsAdminOrSuperAdmin(BasePermission):
    """
    Allows access to admin or superadmin roles.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ["admin", "superadmin"]
        )


# Alias for backward compatibility
IsSuperadminOrAdmin = IsAdminOrSuperAdmin


class IsSuperadmin(BasePermission):
    """Allows access only to superadmin users."""

    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role") and
            request.user.role == "superadmin"
        )


class IsAdmin(BasePermission):
    """Allows access only to admin users."""

    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role") and
            request.user.role == "admin"
        )


class IsSupport(BasePermission):
    """Allows access only to support users."""

    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role") and
            request.user.role == "support"
        )


class IsClient(BasePermission):
    """Allows access only to client users."""

    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role") and
            request.user.role == "client"
        )


class IsWriter(BasePermission):
    """Allows access only to writer users."""

    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role") and
            request.user.role == "writer"
        )


class IsEditor(BasePermission):
    """Allows access only to editor users."""

    def has_permission(self, request, view):
        return (
            hasattr(request.user, "role") and
            request.user.role == "editor"
        )


def IsInRole(allowed_roles):
    """
    Returns a permission class checking if user's role is in allowed_roles.

    Usage:
        permission_classes = [IsInRole(["admin", "support"])]
    """
    class _IsInRole(BasePermission):
        def has_permission(self, request, view):
            return (
                hasattr(request.user, "role") and
                request.user.role in allowed_roles
            )
    return _IsInRole


class IsOrderOwnerOrSupport(BasePermission):
    """
    Allows access to the owner of the order or support/admin/superadmin.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        user_role = getattr(request.user, "role", None)
        support_roles = {"support", "admin", "superadmin"}

        return (
            obj.client == request.user or
            user_role in support_roles
        )
