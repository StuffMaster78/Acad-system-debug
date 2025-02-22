from rest_framework.permissions import BasePermission

class IsEditor(BasePermission):
    """
    Allows access only to editor users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "editor"