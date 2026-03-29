from accounts.selectors.account_role_selector import AccountRoleSelector
from accounts.selectors.account_selector import AccountSelector


class AccountSummarySelector:
    """Builds summary payloads for account profile reads."""

    @staticmethod
    def build_summary(*, website, user) -> dict:
        """Return a structured account summary."""
        account_profile = AccountSelector.get_account_profile_with_roles(
            website=website,
            user=user,
        )

        active_roles = AccountRoleSelector.get_active_roles(
            account_profile=account_profile,
        )

        return {
            "account_profile_id": account_profile.id,
            "website_id": account_profile.website_id,
            "user_id": account_profile.user_id,
            "status": account_profile.status,
            "onboarding_status": account_profile.onboarding_status,
            "is_primary": account_profile.is_primary,
            "activated_at": account_profile.activated_at,
            "suspended_at": account_profile.suspended_at,
            "suspension_reason": account_profile.suspension_reason,
            "roles": [
                {
                    "id": account_role.role.id,
                    "key": account_role.role.key,
                    "name": account_role.role.name,
                    "is_system_role": account_role.role.is_system_role,
                }
                for account_role in active_roles
            ],
            "metadata": account_profile.metadata,
            "created_at": account_profile.created_at,
            "updated_at": account_profile.updated_at,
        }