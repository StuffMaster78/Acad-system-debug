from rest_framework.permissions import BasePermission

class IsSuperadminOnly(BasePermission):
    """
    Allows access only to superadmins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
    
class IsSupportOrAdmin(BasePermission):
    """
    Allow only support or admin staff.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.role in ['admin', 'support']
        )


class IsAssignedWriter(BasePermission):
    """
    Allow only the writer assigned to this order.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.writer


class IsClientWhoOwnsOrder(BasePermission):
    """
    Allow only the client who placed the order.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.client