from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from authentication.services.magic_link_service import MagicLinkService
from authentication.services.password_reset_service import (
    PasswordResetService,
)

User = get_user_model()


class SupportAuthLinkService:
    """
    Generate support-facing auth links for a target user.

    Support/admin can generate links for troubleshooting, but the user
    still uses the link themselves.
    """

    @staticmethod
    def generate_magic_link(
        *,
        target_user,
        website,
        created_by,
    ) -> dict:
        if website is None:
            raise ValidationError("Website context is required.")

        service = MagicLinkService(
            user=target_user,
            website=website,
        )
        _magic_link, _raw_token, magic_url = service.create_magic_link(
            created_by=created_by,
            email=target_user.email,
            expiry_minutes=service.DEFAULT_EXPIRY_MINUTES,
        )

        return {
            "success": True,
            "user_id": target_user.pk,
            "magic_url": magic_url,
            "expires_minutes": service.DEFAULT_EXPIRY_MINUTES,
        }

    @staticmethod
    def generate_password_reset_link(
        *,
        target_user,
        website,
    ) -> dict:
        if website is None:
            raise ValidationError("Website context is required.")

        service = PasswordResetService(
            user=target_user,
            website=website,
        )
        _reset_request, raw_token, raw_otp, reset_link = (
            service.create_reset_request()
        )

        return {
            "success": True,
            "user_id": target_user.pk,
            "reset_link": reset_link,
            "otp_code": raw_otp,
            "token": raw_token,
            "expires_hours": service.TOKEN_EXPIRATION_HOURS,
        }