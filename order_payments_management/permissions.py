from rest_framework import permissions

class IsSuperadminOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only Superadmins and Admins to perform certain actions.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "superadmin"]

    def has_object_permission(self, request, view, obj):
        # Ensures Admins and Superadmins can perform actions on specific objects
        return request.user.is_authenticated and request.user.role in ["admin", "superadmin"]