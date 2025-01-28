from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrSuperAdmin(BasePermission):
    """
    Custom permission to allow access only to admins or superadmins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']


class IsWriter(BasePermission):
    """
    Custom permission to allow access only to writers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'writer'


class IsAdminOrSuperAdminOrReadOnly(BasePermission):
    """
    Custom permission to allow admins or superadmins full access, but 
    read-only access to others.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ['admin', 'superadmin']