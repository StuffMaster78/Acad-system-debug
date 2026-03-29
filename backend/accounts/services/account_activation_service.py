from django.db import transaction
from django.utils import timezone

from accounts.enums import AccountAuditEventType, AccountStatus
from accounts.models import AccountProfile
from accounts.services.account_audit_service import AccountAuditService
from accounts.services.account_status_service import AccountStatusService


class AccountActivationService:
    """Service for named account lifecycle actions."""

    @staticmethod
    @transaction.atomic
    def activate_account(
        *,
        account_profile: AccountProfile,
        actor=None,
        reason: str = "Account activated.",
        metadata: dict | None = None,
    ) -> AccountProfile:
        """Activate an account profile."""
        updated_profile = AccountStatusService.transition_status(
            account_profile=account_profile,
            new_status=AccountStatus.ACTIVE,
            actor=actor,
            reason=reason,
            metadata=metadata,
        )

        updated_profile.activated_at = timezone.now()
        updated_profile.suspended_at = None
        updated_profile.suspension_reason = ""
        updated_profile.save(
            update_fields=[
                "activated_at",
                "suspended_at",
                "suspension_reason",
                "updated_at",
            ]
        )

        AccountAuditService.log_event(
            account_profile=updated_profile,
            event_type=AccountAuditEventType.ACCOUNT_ACTIVATED,
            description=reason,
            actor=actor,
            metadata=metadata,
        )

        return updated_profile

    @staticmethod
    @transaction.atomic
    def suspend_account(
        *,
        account_profile: AccountProfile,
        reason: str,
        actor=None,
        metadata: dict | None = None,
    ) -> AccountProfile:
        """Suspend an account profile."""
        updated_profile = AccountStatusService.transition_status(
            account_profile=account_profile,
            new_status=AccountStatus.SUSPENDED,
            actor=actor,
            reason=reason,
            metadata=metadata,
        )

        updated_profile.suspended_at = timezone.now()
        updated_profile.suspension_reason = reason
        updated_profile.save(
            update_fields=[
                "suspended_at",
                "suspension_reason",
                "updated_at",
            ]
        )

        AccountAuditService.log_event(
            account_profile=updated_profile,
            event_type=AccountAuditEventType.ACCOUNT_SUSPENDED,
            description=reason,
            actor=actor,
            metadata=metadata,
        )

        return updated_profile

    @staticmethod
    @transaction.atomic
    def reactivate_account(
        *,
        account_profile: AccountProfile,
        actor=None,
        reason: str = "Account reactivated.",
        metadata: dict | None = None,
    ) -> AccountProfile:
        """Reactivate a suspended account profile."""
        updated_profile = AccountStatusService.transition_status(
            account_profile=account_profile,
            new_status=AccountStatus.ACTIVE,
            actor=actor,
            reason=reason,
            metadata=metadata,
        )

        updated_profile.suspended_at = None
        updated_profile.suspension_reason = ""
        updated_profile.save(
            update_fields=[
                "suspended_at",
                "suspension_reason",
                "updated_at",
            ]
        )

        AccountAuditService.log_event(
            account_profile=updated_profile,
            event_type=AccountAuditEventType.ACCOUNT_REACTIVATED,
            description=reason,
            actor=actor,
            metadata=metadata,
        )

        return updated_profile