from accounts.models import AccountProfile
from accounts.selectors.account_selector import AccountSelector
from accounts.selectors.account_summary_selector import (
    AccountSummarySelector,
)
from accounts.services.account_creation_service import AccountCreationService


class AccountService:
    """High level service for account profile workflows."""

    @staticmethod
    def get_or_create_account_profile(
        *,
        website,
        user,
        actor=None,
        is_primary: bool = False,
        metadata: dict | None = None,
    ) -> AccountProfile:
        """Fetch an existing account profile or create one."""
        try:
            return AccountSelector.get_account_profile(
                website=website,
                user=user,
            )
        except AccountProfile.DoesNotExist:
            return AccountCreationService.create_account_profile(
                website=website,
                user=user,
                actor=actor,
                is_primary=is_primary,
                metadata=metadata,
            )

    @staticmethod
    def get_account_summary(*, website, user) -> dict:
        """Return a summarized account view for a website user."""
        return AccountSummarySelector.build_summary(
            website=website,
            user=user,
        )