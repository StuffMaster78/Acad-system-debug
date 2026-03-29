from accounts.enums import AccountStatus
from accounts.models import AccountProfile, AccountStatusHistory
from accounts.validators.account_status_validator import (
    AccountStatusValidator,
)


class AccountStatusService:
    """Service for generic account status transitions."""

    @staticmethod
    def transition_status(
        *,
        account_profile: AccountProfile,
        new_status: AccountStatus,
        actor=None,
        reason: str = "",
        metadata: dict | None = None,
    ) -> AccountProfile:
        """Move an account profile from one status to another."""
        old_status = AccountStatus(account_profile.status)

        AccountStatusValidator.validate_transition(
            current_status=old_status,
            new_status=new_status,
        )

        account_profile.status = new_status
        account_profile.save(update_fields=["status", "updated_at"])

        AccountStatusHistory.objects.create(
            website=account_profile.website,
            account_profile=account_profile,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            changed_by=actor,
            metadata=metadata or {},
        )

        return account_profile