from django.db import transaction

from accounts.enums import AccountAuditEventType
from accounts.exceptions import AccountProfileAlreadyExistsError
from accounts.models import AccountProfile
from accounts.services.account_audit_service import AccountAuditService


class AccountCreationService:
    """Service for creating account profiles."""

    @staticmethod
    @transaction.atomic
    def create_account_profile(
        *,
        website,
        user,
        actor=None,
        is_primary: bool = False,
        metadata: dict | None = None,
    ) -> AccountProfile:
        """Create an account profile for a website and user."""
        if AccountProfile.objects.filter(
            website=website,
            user=user,
        ).exists():
            raise AccountProfileAlreadyExistsError(
                "Account profile already exists for this website and user."
            )

        account_profile = AccountProfile.objects.create(
            website=website,
            user=user,
            is_primary=is_primary,
            metadata=metadata or {},
        )

        AccountAuditService.log_event(
            account_profile=account_profile,
            event_type=AccountAuditEventType.ACCOUNT_CREATED,
            description="Account profile created.",
            actor=actor,
        )

        return account_profile