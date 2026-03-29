from accounts.models import AccountRole


class AccountRoleSelector:
    """Read helpers for account role queries."""

    @staticmethod
    def get_active_roles(*, account_profile):
        """Return active roles for an account profile."""
        return AccountRole.objects.filter(
            account_profile=account_profile,
            is_active=True,
        ).select_related("role")

    @staticmethod
    def has_role(*, account_profile, role_key: str) -> bool:
        """Check whether an account profile has an active role."""
        return AccountRole.objects.filter(
            account_profile=account_profile,
            is_active=True,
            role__key=role_key,
        ).exists()