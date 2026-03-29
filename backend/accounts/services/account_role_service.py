from django.db import transaction

from accounts.enums import AccountAuditEventType
from accounts.exceptions import (
    InactiveRoleDefinitionError,
    RoleAlreadyAssignedError,
    RoleNotAssignedError,
)
from accounts.models import AccountProfile, AccountRole, RoleDefinition
from accounts.services.account_audit_service import AccountAuditService


class AccountRoleService:
    """Service for assigning and revoking account roles."""

    @staticmethod
    def get_role_definition_by_key(
        *,
        website,
        role_key: str,
        active_only: bool = False,
    ) -> RoleDefinition:
        """Resolve a role definition for a website by key."""
        filters = {
            "website": website,
            "key": role_key,
        }
        if active_only:
            filters["is_active"] = True

        return RoleDefinition.objects.get(**filters)

    @staticmethod
    @transaction.atomic
    def assign_role(
        *,
        account_profile: AccountProfile,
        role: RoleDefinition,
        actor=None,
        metadata: dict | None = None,
    ) -> AccountRole:
        """Assign a role to an account profile."""
        if not role.is_active:
            raise InactiveRoleDefinitionError(
                "Cannot assign an inactive role definition."
            )

        existing_role = AccountRole.objects.filter(
            account_profile=account_profile,
            role=role,
        ).first()

        if existing_role:
            if existing_role.is_active:
                raise RoleAlreadyAssignedError(
                    "Role is already assigned to this account profile."
                )

            existing_role.is_active = True
            existing_role.assigned_by = actor
            existing_role.metadata = metadata or existing_role.metadata
            existing_role.save(
                update_fields=["is_active", "assigned_by", "metadata"]
            )
            assigned_role = existing_role
        else:
            assigned_role = AccountRole.objects.create(
                website=account_profile.website,
                account_profile=account_profile,
                role=role,
                assigned_by=actor,
                metadata=metadata or {},
            )

        AccountAuditService.log_event(
            account_profile=account_profile,
            event_type=AccountAuditEventType.ROLE_ASSIGNED,
            description=f"Assigned role '{role.key}'.",
            actor=actor,
            metadata={"role_key": role.key},
        )

        return assigned_role

    @staticmethod
    @transaction.atomic
    def assign_role_by_key(
        *,
        account_profile: AccountProfile,
        role_key: str,
        actor=None,
        metadata: dict | None = None,
    ) -> AccountRole:
        """Resolve and assign a role by role key."""
        role = AccountRoleService.get_role_definition_by_key(
            website=account_profile.website,
            role_key=role_key,
            active_only=True,
        )
        return AccountRoleService.assign_role(
            account_profile=account_profile,
            role=role,
            actor=actor,
            metadata=metadata,
        )

    @staticmethod
    @transaction.atomic
    def revoke_role(
        *,
        account_profile: AccountProfile,
        role: RoleDefinition,
        actor=None,
        metadata: dict | None = None,
    ) -> AccountRole:
        """Revoke a role from an account profile."""
        account_role = AccountRole.objects.filter(
            account_profile=account_profile,
            role=role,
            is_active=True,
        ).first()

        if not account_role:
            raise RoleNotAssignedError(
                "Role is not actively assigned to this account profile."
            )

        account_role.is_active = False
        account_role.metadata = metadata or account_role.metadata
        account_role.save(update_fields=["is_active", "metadata"])

        AccountAuditService.log_event(
            account_profile=account_profile,
            event_type=AccountAuditEventType.ROLE_REVOKED,
            description=f"Revoked role '{role.key}'.",
            actor=actor,
            metadata={"role_key": role.key},
        )

        return account_role

    @staticmethod
    @transaction.atomic
    def revoke_role_by_key(
        *,
        account_profile: AccountProfile,
        role_key: str,
        actor=None,
        metadata: dict | None = None,
    ) -> AccountRole:
        """Resolve and revoke a role by role key."""
        role = AccountRoleService.get_role_definition_by_key(
            website=account_profile.website,
            role_key=role_key,
            active_only=False,
        )
        return AccountRoleService.revoke_role(
            account_profile=account_profile,
            role=role,
            actor=actor,
            metadata=metadata,
        )