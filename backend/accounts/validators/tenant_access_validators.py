from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError

from accounts.models import TenantAccess
from websites.models.websites import Website


class TenantAccessValidators:
    """
    Validation helpers for tenant access.
    """

    @staticmethod
    def validate_website_is_active(
        *,
        website: Website,
    ) -> None:
        is_active = getattr(website, "is_active", True)

        if not is_active:
            raise ValidationError(
                "Cannot grant access to an inactive website."
            )

    @staticmethod
    def validate_user_does_not_have_active_access(
        *,
        user: Any,
        website: Website,
    ) -> None:
        exists = TenantAccess.objects.filter(
            user=user,
            website=website,
            is_active=True,
        ).exists()

        if exists:
            raise ValidationError(
                "User already has active access to this tenant."
            )