from __future__ import annotations

from typing import Any

from django.db import transaction

from accounts.models import AccountProfile, AccountRole, RoleDefinition
from accounts.services.portal_access_service import PortalAccessService
from accounts.services.tenant_access_service import TenantAccessService


class AccountAccessProvisioningService:
    """
    Creates the correct access package for a user.

    This avoids manually assigning:
        role
        portal
        tenant access

    every time a user is created.
    """

    @staticmethod
    @transaction.atomic
    def provision_client(
        *,
        user: Any,
        website: Any,
        granted_by: Any | None = None,
    ) -> AccountProfile:
        account = AccountAccessProvisioningService._get_or_create_account(
            user=user,
            website=website,
            account_type="client",
        )

        AccountAccessProvisioningService._assign_role(
            account=account,
            role_key="client",
        )

        PortalAccessService.grant_portal_access(
            user=user,
            portal_code="client_portal",
            granted_by=granted_by,
        )

        TenantAccessService.grant_access(
            user=user,
            website=website,
            granted_by=granted_by,
        )

        return account

    @staticmethod
    @transaction.atomic
    def provision_writer(
        *,
        user: Any,
        website: Any,
        granted_by: Any | None = None,
    ) -> AccountProfile:
        account = AccountAccessProvisioningService._get_or_create_account(
            user=user,
            website=website,
            account_type="writer",
        )

        AccountAccessProvisioningService._assign_role(
            account=account,
            role_key="writer",
        )

        PortalAccessService.grant_portal_access(
            user=user,
            portal_code="writer_portal",
            granted_by=granted_by,
        )

        TenantAccessService.grant_access(
            user=user,
            website=website,
            granted_by=granted_by,
        )

        return account

    @staticmethod
    @transaction.atomic
    def provision_staff(
        *,
        user: Any,
        website: Any,
        role_key: str,
        granted_by: Any | None = None,
    ) -> AccountProfile:
        account = AccountAccessProvisioningService._get_or_create_account(
            user=user,
            website=website,
            account_type=role_key,
        )

        AccountAccessProvisioningService._assign_role(
            account=account,
            role_key=role_key,
        )

        PortalAccessService.grant_portal_access(
            user=user,
            portal_code="internal_admin",
            granted_by=granted_by,
        )

        TenantAccessService.grant_access(
            user=user,
            website=website,
            granted_by=granted_by,
        )

        return account

    @staticmethod
    @transaction.atomic
    def provision_superadmin(
        *,
        user: Any,
        granted_by: Any | None = None,
    ) -> AccountProfile:
        account = AccountAccessProvisioningService._get_or_create_account(
            user=user,
            website=None,
            account_type="superadmin",
        )

        AccountAccessProvisioningService._assign_role(
            account=account,
            role_key="superadmin",
        )

        PortalAccessService.grant_portal_access(
            user=user,
            portal_code="internal_admin",
            granted_by=granted_by,
        )

        return account

    @staticmethod
    def _get_or_create_account(
        *,
        user: Any,
        website: Any | None,
        account_type: str,
    ) -> AccountProfile:
        account, _created = AccountProfile.objects.get_or_create(
            user=user,
            website=website,
            defaults={
                "account_type": account_type,
                "status": "active",
            },
        )

        return account

    @staticmethod
    def _assign_role(
        *,
        account: AccountProfile,
        role_key: str,
    ) -> AccountRole:
        role = RoleDefinition.objects.get(
            key=role_key,
            is_active=True,
        )

        account_role, _created = AccountRole.objects.get_or_create(
            account=account,
            role=role,
            defaults={
                "is_active": True,
            },
        )

        if not account_role.is_active:
            account_role.is_active = True
            account_role.save(update_fields=["is_active"])

        return account_role