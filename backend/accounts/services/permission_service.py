from __future__ import annotations

from typing import Any, Set

from accounts.models import AccountRole, RolePermission


class AccountPermissionService:
    """
    Central permission evaluation service.

    Decides what an authenticated user can do.
    """

    @staticmethod
    def _get_user_role_ids(
        *,
        user: Any,
        website: Any | None = None,
    ) -> Set[int]:
        qs = AccountRole.objects.filter(
            account__user=user,
            is_active=True,
        )

        if website is not None:
            qs = qs.filter(account__website=website)

        return set(qs.values_list("role_id", flat=True))

    @staticmethod
    def get_user_permissions(
        *,
        user: Any,
        website: Any | None = None,
    ) -> Set[str]:
        role_ids = AccountPermissionService._get_user_role_ids(
            user=user,
            website=website,
        )

        if not role_ids:
            return set()

        permissions = RolePermission.objects.filter(
            role_id__in=role_ids,
            is_active=True,
            permission__is_active=True,
        ).select_related("permission")

        return {role_permission.permission.code for role_permission in permissions}

    @staticmethod
    def user_has_permission(
        *,
        user: Any,
        permission_code: str,
        website: Any | None = None,
    ) -> bool:
        permissions = AccountPermissionService.get_user_permissions(
            user=user,
            website=website,
        )

        return permission_code in permissions

    @staticmethod
    def require_permission(
        *,
        user: Any,
        permission_code: str,
        website: Any | None = None,
    ) -> None:
        has_permission = AccountPermissionService.user_has_permission(
            user=user,
            permission_code=permission_code,
            website=website,
        )

        if not has_permission:
            raise PermissionError(
                f"User lacks permission: {permission_code}"
            )