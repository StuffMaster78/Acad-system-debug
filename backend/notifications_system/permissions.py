from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUser(BasePermission):
    """
    Allows access only to superusers.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsAdminOrReadOnly(BasePermission):
    """
    Allows access only to admin/staff users for unsafe methods.
    Safe methods (GET, HEAD, OPTIONS) are open.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Allows access only to authenticated users for unsafe methods.
    Safe methods (GET, HEAD, OPTIONS) are open.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)
    

class IsAdminUser(BasePermission):
    """
    Allows access only to admin/staff users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)