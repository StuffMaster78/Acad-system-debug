from typing import Any, cast

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models.login_session import LoginSession
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService,
)
from authentication.services.login_session_service import (
    LoginSessionService,
)

User = get_user_model()


class RefreshTokenPolicyService:
    """
    Validate whether a refresh token may be used to issue new tokens.
    """

    @staticmethod
    def validate_refresh(
        *,
        raw_refresh_token: str,
        request=None,
    ) -> tuple[RefreshToken, object, LoginSession]:
        """
        Validate refresh token against session, user, website, and
        impersonation policy.

        Returns:
            Tuple of:
                - parsed RefreshToken
                - resolved user
                - resolved LoginSession

        Raises:
            InvalidToken: If validation fails.
        """
        try:
            refresh = RefreshToken(cast(Any, raw_refresh_token))
        except Exception as exc:
            raise InvalidToken("Invalid refresh token.") from exc

        user_id = refresh.get("user_id")
        session_id_raw = refresh.get("session_id")
        website_id_raw = refresh.get("website_id")
        is_impersonation = bool(refresh.get("is_impersonation", False))

        if user_id is None:
            raise InvalidToken("Refresh token missing user identifier.")

        session_id = RefreshTokenPolicyService._coerce_int(
            session_id_raw,
            field_name="session_id",
        )
        website_id = RefreshTokenPolicyService._coerce_optional_int(
            website_id_raw,
            field_name="website_id",
        )

        user = User.objects.filter(pk=user_id).first()
        if user is None:
            raise InvalidToken("User not found.")

        request_website = getattr(request, "website", None)
        if request_website is not None and website_id is not None:
            if request_website.pk != website_id:
                raise InvalidToken("Cross-tenant refresh denied.")

        website = request_website
        if website is None and website_id is not None:
            website = getattr(user, "website", None)
            if website is None or website.pk != website_id:
                raise InvalidToken("Website context mismatch.")

        if website is None:
            website = getattr(user, "website", None)

        if website is None:
            raise InvalidToken("Website context is required.")

        AccountAccessPolicyService.validate_auth_access(
            user=user,
            website=website,
        )

        session = LoginSessionService.get_session_by_id(
            session_id=session_id,
            user=user,
            website=website,
        )

        if session is None:
            raise InvalidToken("Session not found.")

        was_revoked = LoginSessionService.revoke_if_expired(
            session=session,
        )
        if was_revoked:
            raise InvalidToken("Session has expired or was revoked.")

        if is_impersonation:
            if session.session_type != LoginSession.SessionType.IMPERSONATION:
                raise InvalidToken("Invalid impersonation session.")
        else:
            if session.session_type == LoginSession.SessionType.IMPERSONATION:
                raise InvalidToken("Impersonation session mismatch.")

        return refresh, user, session

    @staticmethod
    def _coerce_int(value, *, field_name: str) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        raise InvalidToken(f"Invalid {field_name} claim.")

    @staticmethod
    def _coerce_optional_int(value, *, field_name: str) -> int | None:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        raise InvalidToken(f"Invalid {field_name} claim.")