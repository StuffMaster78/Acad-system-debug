from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Allows access to admin users for unsafe methods (POST, PUT, DELETE).
    Read-only access for other users.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff


class IsClient(BasePermission):
    """
    Allows access only to users with the 'client' role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to allow only the owner of an object or admin users to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admins have access to all objects
        if request.user.is_staff:
            return True

        # Object-level permission: Check if the user is the owner
        return obj.client.user == request.user