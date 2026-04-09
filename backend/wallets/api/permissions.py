from rest_framework.permissions import BasePermission


class IsWalletAdminOrSuperAdmin(BasePermission):
    """
    Replace role checks with your real permission system.
    """

    message = "You do not have permission to manage wallets."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser or user.is_staff:
            return True

        role = getattr(user, "role", None)
        return role in {"admin", "superadmin", "support"}