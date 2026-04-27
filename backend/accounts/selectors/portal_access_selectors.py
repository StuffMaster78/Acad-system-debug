from __future__ import annotations

from typing import Any

from accounts.models import PortalAccess, PortalDefinition


class PortalAccessSelectors:
    """
    Read helpers for portal access.
    """

    @staticmethod
    def get_active_portals_for_user(
        *,
        user: Any,
    ):
        return PortalDefinition.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
            is_active=True,
        ).order_by("code")

    @staticmethod
    def get_active_portal_codes_for_user(
        *,
        user: Any,
    ) -> set[str]:
        portals = PortalAccessSelectors.get_active_portals_for_user(
            user=user,
        )

        return set(portals.values_list("code", flat=True))

    @staticmethod
    def get_user_portal_access_records(
        *,
        user: Any,
    ):
        return PortalAccess.objects.filter(
            user=user,
        ).select_related(
            "portal",
            "granted_by",
        ).order_by("portal__code")