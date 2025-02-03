from rest_framework import permissions


class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a message or admins to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:  # Admins have full access
            return True
        return obj.sender == request.user  # Owners can only edit their own messages


class CanSendOrderMessage(permissions.BasePermission):
    """
    Restricts messaging if the order is archived and no admin override is set.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            thread = view.get_object()
            if not thread.is_active and not thread.admin_override and request.user.profile.role in ["client", "writer"]:
                return False
        return True