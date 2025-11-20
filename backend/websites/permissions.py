from rest_framework import permissions

class IsAdminOrSuperadmin(permissions.BasePermission):
    """
    Allows access only to users who are either Admin or Superadmin.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "superadmin"]