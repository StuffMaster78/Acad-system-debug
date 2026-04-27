from django.db import transaction

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


class StaffOnboardingService:
    """Service for staff role onboarding workflows."""

    @staticmethod
    @transaction.atomic
    def complete_onboarding(
        *,
        account_profile,
        role_keys: list[str],
        actor=None,
        metadata: dict | None = None,
    ):
        """Complete staff onboarding and assign one or more staff roles."""
        session = OnboardingService.start_session(
            website=account_profile.website,
            user=account_profile.user,
            account_profile=account_profile,
            onboarding_type=OnboardingType.STAFF,
            actor=actor,
            metadata=metadata,
        )

        roles = RoleDefinition.objects.filter(
            website=account_profile.website,
            key__in=role_keys,
            is_active=True,
        )

        for role in roles:
            AccountRoleService.assign_role(
                account_profile=account_profile,
                role=role,
                actor=actor,
                metadata=metadata,
            )

        account_profile.onboarding_status = OnboardingStatus.COMPLETED
        account_profile.status = AccountStatus.ACTIVE
        account_profile.save(
            update_fields=["onboarding_status", "status", "updated_at"]
        )

        PortalAccessService.grant_portal_access(
            user=account_profile.user,
            portal_code="internal_admin",
            granted_by=actor,
        )

        TenantAccessService.grant_access(
            user=account_profile.user,
            website=account_profile.website,
            granted_by=actor,
        )

        OnboardingService.complete_session(session=session)

        AccountAuditService.log_event(
            account_profile=account_profile,
            event_type=AccountAuditEventType.STAFF_ONBOARDING_COMPLETED,
            description="Staff onboarding completed.",
            actor=actor,
            metadata={
                **(metadata or {}),
                "role_keys": role_keys,
            },
        )

        return account_profile