from rest_framework.permissions import BasePermission


class IsWriter(BasePermission):
    """
    Allows access only to users with the 'writer' role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'writer'