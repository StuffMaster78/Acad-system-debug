from rest_framework import permissions

class IsSuperadminOnly(permissions.BasePermission):
    """
    Allows access only to superadmins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser