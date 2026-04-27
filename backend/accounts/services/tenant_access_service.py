from __future__ import annotations

from typing import Any
from accounts.models import TenantAccess
from websites.models.websites import Website

class TenantAccessService:
    """
    Controls tenant or website access.

    Examples:
        Gradecrest
        NurseMyGrade
        EssayManiacs
    """

    @staticmethod
    def user_has_access(
        *,
        user: Any,
        website: Website,
    ) -> bool:
        return TenantAccess.objects.filter(
            user=user,
            website=website,
            is_active=True,
        ).exists()

    @staticmethod
    def require_access(
        *,
        user: Any,
        website: Website,
    ) -> None:
        if not TenantAccessService.user_has_access(
            user=user,
            website=website,
        ):
            raise PermissionError(
                f"User has no access to tenant: {website}"
            )

    @staticmethod
    def grant_access(
        *,
        user: Any,
        website: Website,
        granted_by: Any | None = None,
    ) -> TenantAccess:
        access, _ = TenantAccess.objects.get_or_create(
            user=user,
            website=website,
            defaults={
                "granted_by": granted_by,
            },
        )

        if not access.is_active:
            access.is_active = True
            access.save(update_fields=["is_active"])

        return access

    @staticmethod
    def revoke_access(
        *,
        user: Any,
        website: Website,
    ) -> None:
        TenantAccess.objects.filter(
            user=user,
            website=website,
        ).update(is_active=False)