from __future__ import annotations

from typing import Any

from accounts.models import TenantAccess
from websites.models.websites import Website


class TenantAccessSelectors:
    """
    Read helpers for website or tenant access.
    """

    @staticmethod
    def get_active_websites_for_user(
        *,
        user: Any,
    ):
        return Website.objects.filter(
            user_accesses__user=user,
            user_accesses__is_active=True,
        ).order_by("name")

    @staticmethod
    def get_active_website_ids_for_user(
        *,
        user: Any,
    ) -> set[int]:
        websites = TenantAccessSelectors.get_active_websites_for_user(
            user=user,
        )

        return set(websites.values_list("id", flat=True))

    @staticmethod
    def get_user_tenant_access_records(
        *,
        user: Any,
    ):
        return TenantAccess.objects.filter(
            user=user,
        ).select_related(
            "website",
            "granted_by",
        ).order_by("website__name")