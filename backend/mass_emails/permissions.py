from rest_framework.permissions import BasePermission


MASS_EMAIL_STAFF_ROLES = {"superadmin", "admin", "support", "editor"}


class CanManageMassEmails(BasePermission):
    """
    Allow operational staff to manage mass email campaigns.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            getattr(user, "is_superuser", False)
            or getattr(user, "is_staff", False)
            or getattr(user, "role", None) in MASS_EMAIL_STAFF_ROLES
        )


class IsMassEmailAdmin(BasePermission):
    """
    Restrict provider configuration and cross-user history to admin roles.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            getattr(user, "is_superuser", False)
            or getattr(user, "role", None) in {"superadmin", "admin"}
        )
