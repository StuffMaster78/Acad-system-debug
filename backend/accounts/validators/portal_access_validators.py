from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError

from accounts.models import PortalAccess, PortalDefinition


class PortalAccessValidators:
    """
    Validation helpers for portal access.
    """

    @staticmethod
    def validate_portal_exists_and_active(
        *,
        portal_code: str,
    ) -> PortalDefinition:
        try:
            return PortalDefinition.objects.get(
                code=portal_code,
                is_active=True,
            )
        except PortalDefinition.DoesNotExist as exc:
            raise ValidationError(
                f"Active portal '{portal_code}' does not exist."
            ) from exc

    @staticmethod
    def validate_user_does_not_have_active_access(
        *,
        user: Any,
        portal: PortalDefinition,
    ) -> None:
        exists = PortalAccess.objects.filter(
            user=user,
            portal=portal,
            is_active=True,
        ).exists()

        if exists:
            raise ValidationError(
                "User already has active access to this portal."
            )