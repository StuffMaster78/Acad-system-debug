from django.core.exceptions import ValidationError
from django.utils.timezone import now

from authentication.models.secure_token import SecureToken
from authentication.services.token_service import TokenService


class SecureTokenService:
    """
    Manage generic secure token lifecycle.
    """

    @staticmethod
    def create_token(
        *,
        user,
        website,
        purpose: str,
        expires_at,
    ) -> tuple[SecureToken, str]:
        raw_token, token_hash = TokenService.generate_hashed_token()

        token = SecureToken.objects.create(
            user=user,
            website=website,
            token_hash=token_hash,
            purpose=purpose,
            expires_at=expires_at,
        )

        return token, raw_token

    @staticmethod
    def validate_token(
        *,
        user,
        website,
        raw_token: str,
        purpose: str,
    ) -> SecureToken:
        token_hash = TokenService.hash_value(raw_token)

        try:
            token = SecureToken.objects.get(
                user=user,
                website=website,
                token_hash=token_hash,
                purpose=purpose,
                revoked_at__isnull=True,
            )
        except SecureToken.DoesNotExist as exc:
            raise ValidationError("Invalid token.") from exc

        if token.is_expired:
            raise ValidationError("Token has expired.")

        return token

    @staticmethod
    def consume_token(
        *,
        token: SecureToken,
        revoke_after_use: bool = True,
    ) -> SecureToken:
        token.mark_as_used()

        if revoke_after_use:
            token.revoke()

        return token