from django.db import transaction

from accounts.constants import DEFAULT_WRITER_ROLE
from accounts.enums import (
    AccountAuditEventType,
    AccountStatus,
    OnboardingStatus,
    OnboardingType,
)
from accounts.models import RoleDefinition
from accounts.services.account_audit_service import AccountAuditService
from accounts.services.account_role_service import AccountRoleService
from accounts.services.onboarding_service import OnboardingService
from accounts.services.portal_access_service import PortalAccessService
from accounts.services.tenant_access_service import TenantAccessService


class WriterOnboardingService:
    """Service for writer specific onboarding workflows."""

    @staticmethod
    @transaction.atomic
    def complete_onboarding(
        *,
        account_profile,
        actor=None,
        metadata: dict | None = None,
        require_review: bool = True,
    ):
        """Complete writer onboarding for an account profile."""
        role = RoleDefinition.objects.get(
            website=account_profile.website,
            key=DEFAULT_WRITER_ROLE,
        )

        session = OnboardingService.start_session(
            website=account_profile.website,
            user=account_profile.user,
            account_profile=account_profile,
            onboarding_type=OnboardingType.WRITER,
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

        PortalAccessService.grant_portal_access(
            user=account_profile.user,
            portal_code="writer_portal",
            granted_by=actor,
        )

        TenantAccessService.grant_access(
            user=account_profile.user,
            website=account_profile.website,
            granted_by=actor,
        )

        account_profile.onboarding_status = OnboardingStatus.COMPLETED
        account_profile.status = (
            AccountStatus.UNDER_REVIEW
            if require_review
            else AccountStatus.ACTIVE
        )
        account_profile.save(
            update_fields=["onboarding_status", "status", "updated_at"]
        )

        OnboardingService.complete_session(session=session)

        AccountAuditService.log_event(
            account_profile=account_profile,
            event_type=AccountAuditEventType.WRITER_ONBOARDING_COMPLETED,
            description="Writer onboarding completed.",
            actor=actor,
            metadata={
                **(metadata or {}),
                "require_review": require_review,
            },
        )

        return account_profile