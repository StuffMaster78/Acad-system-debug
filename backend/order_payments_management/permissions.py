from rest_framework import permissions

class IsSuperadminOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only Superadmins and Admins to perform certain actions.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            getattr(user, 'role', None) in ["admin", "superadmin"] or getattr(user, 'is_staff', False)
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated and (
            getattr(user, 'role', None) in ["admin", "superadmin"] or getattr(user, 'is_staff', False)
        )