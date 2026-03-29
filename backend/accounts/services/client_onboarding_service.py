from django.db import transaction

from accounts.constants import DEFAULT_CLIENT_ROLE
from accounts.enums import (
    AccountAuditEventType,
    OnboardingStatus,
    OnboardingType,
)
from accounts.models import RoleDefinition
from accounts.services.account_audit_service import AccountAuditService
from accounts.services.account_role_service import AccountRoleService
from accounts.services.onboarding_service import OnboardingService


class ClientOnboardingService:
    """Service for client specific onboarding workflows."""

    @staticmethod
    @transaction.atomic
    def complete_onboarding(
        *,
        account_profile,
        actor=None,
        metadata: dict | None = None,
    ):
        """Complete client onboarding for an account profile."""
        role = RoleDefinition.objects.get(
            website=account_profile.website,
            key=DEFAULT_CLIENT_ROLE,
        )

        session = OnboardingService.start_session(
            website=account_profile.website,
            user=account_profile.user,
            account_profile=account_profile,
            onboarding_type=OnboardingType.CLIENT,
            target_role=role,
            actor=actor,
            metadata=metadata,
        )

        AccountRoleService.assign_role(
            account_profile=account_profile,
            role=role,
            actor=actor,
            metadata=metadata,
        )

        account_profile.onboarding_status = OnboardingStatus.COMPLETED
        account_profile.save(update_fields=["onboarding_status", "updated_at"])

        OnboardingService.complete_session(session=session)

        AccountAuditService.log_event(
            account_profile=account_profile,
            event_type=AccountAuditEventType.CLIENT_ONBOARDING_COMPLETED,
            description="Client onboarding completed.",
            actor=actor,
            metadata=metadata,
        )

        return account_profile