from __future__ import annotations

from typing import Any

from accounts.models import AccountRole, PermissionDefinition, RolePermission


class PermissionSelectors:
    """
    Read helpers for account permissions.
    """

    @staticmethod
    def get_active_permission_codes_for_user(
        *,
        user: Any,
        website: Any | None = None,
    ) -> set[str]:
        account_roles = AccountRole.objects.filter(
            account__user=user,
            is_active=True,
        )

        if website is not None:
            account_roles = account_roles.filter(account__website=website)

        role_ids = account_roles.values_list("role_id", flat=True)

        permissions = RolePermission.objects.filter(
            role_id__in=role_ids,
            is_active=True,
            permission__is_active=True,
        ).select_related("permission")

        return {item.permission.code for item in permissions}

    @staticmethod
    def get_permissions_for_role(
        *,
        role: Any,
    ):
        return PermissionDefinition.objects.filter(
            permission_roles__role=role,
            permission_roles__is_active=True,
            is_active=True,
        ).order_by("code")