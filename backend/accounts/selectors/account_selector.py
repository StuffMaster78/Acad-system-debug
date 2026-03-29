from django.db.models import Prefetch

from accounts.models import AccountProfile, AccountRole


class AccountSelector:
    """Read helpers for account profile data."""

    @staticmethod
    def get_account_profile(*, website, user) -> AccountProfile:
        """Fetch an account profile for a given website and user."""
        return AccountProfile.objects.select_related(
            "website",
            "user",
        ).get(
            website=website,
            user=user,
        )

    @staticmethod
    def get_account_profile_with_roles(*, website, user) -> AccountProfile:
        """Fetch an account profile with active role assignments."""
        active_roles = AccountRole.objects.filter(is_active=True).select_related(
            "role"
        )

        return AccountProfile.objects.select_related(
            "website",
            "user",
        ).prefetch_related(
            Prefetch("roles", queryset=active_roles)
        ).get(
            website=website,
            user=user,
        )
    

    @staticmethod
    def get_account_profile_by_id(*, website, account_profile_id: int):
        """Fetch an account profile by ID within a website."""
        return AccountProfile.objects.select_related(
            "website",
            "user",
        ).get(
            website=website,
            id=account_profile_id,
        )