from rest_framework.permissions import IsAuthenticated


class IsTenantStaff(IsAuthenticated):
    """
    Allows authenticated tenant staff, admins, superadmins, and content
    managers to access file management operations.
    """

    def has_permission(self, request, view) -> bool:
        """
        Return whether the request user can manage tenant files.
        """

        if not super().has_permission(request, view):
            return False

        user = request.user

        return bool(
            getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
            or getattr(user, "is_admin", False)
            or getattr(user, "is_super_admin", False)
            or getattr(user, "is_content_manager", False)
        )