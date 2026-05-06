from rest_framework.permissions import BasePermission


class IsAuditViewer(BasePermission):
    """
    Only internal staff / admins should access audit API.
    """

    def has_permission( # type: ignore[override]
            self,
            request,
            view
        ) -> bool:  
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )