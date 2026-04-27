from __future__ import annotations

from typing import Any

from accounts.models.portal_definition import PortalDefinition
from accounts.models.portal_access import PortalAccess

class PortalAccessService:
    """
    Controls portal access.

    Examples:
        internal_admin
        writer_portal
        client_portal
    """

    @staticmethod
    def user_has_portal_access(
        *,
        user: Any,
        portal_code: str,
    ) -> bool:
        return PortalAccess.objects.filter(
            user=user,
            portal__code=portal_code,
            is_active=True,
            portal__is_active=True,
        ).exists()

    @staticmethod
    def require_portal_access(
        *,
        user: Any,
        portal_code: str,
    ) -> None:
        if not PortalAccessService.user_has_portal_access(
            user=user,
            portal_code=portal_code,
        ):
            raise PermissionError(
                f"User has no access to portal: {portal_code}"
            )

    @staticmethod
    def grant_portal_access(
        *,
        user: Any,
        portal_code: str,
        granted_by: Any | None = None,
    ) -> PortalAccess:
        portal = PortalDefinition.objects.get(code=portal_code)

        access, _ = PortalAccess.objects.get_or_create(
            user=user,
            portal=portal,
            defaults={
                "granted_by": granted_by,
            },
        )

        if not access.is_active:
            access.is_active = True
            access.save(update_fields=["is_active"])

        return access

    @staticmethod
    def revoke_portal_access(
        *,
        user: Any,
        portal_code: str,
    ) -> None:
        PortalAccess.objects.filter(
            user=user,
            portal__code=portal_code,
        ).update(is_active=False)