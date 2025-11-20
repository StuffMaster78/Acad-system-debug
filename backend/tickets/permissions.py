from rest_framework import permissions

class IsAdminOrSupportForAttachment(permissions.BasePermission):
    """
    Only superadmin, admin, or support can download attachments.
    """

    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and (
                getattr(user, 'role', None) in ['superadmin', 'admin', 'support']
            )
        )