from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Allows access only to superusers.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class IsAdminOrReadOnly(BasePermission):
    """
    Allows access only to admin users for unsafe methods (POST, PUT, DELETE).
    """
    def has_permission(self, request, view):
        if request.method in ["POST", "PUT", "DELETE"]:
            return bool(request.user and request.user.is_staff)
        return True
    
class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Allows access only to authenticated users for unsafe methods (POST, PUT, DELETE).
    """
    def has_permission(self, request, view):
        if request.method in ["POST", "PUT", "DELETE"]:
            return bool(request.user and request.user.is_authenticated)
        return True