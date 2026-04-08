from datetime import timedelta
from django.utils import timezone
from typing import Any
from django.db.models import Q

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.timezone import now

from authentication.models.login_session import LoginSession
from authentication.services.token_service import TokenService


class LoginSessionService:
    """
    Handle authenticated session lifecycle management.

    This service is responsible for:
        - starting login sessions
        - revoking individual sessions
        - revoking all sessions for a user
        - resolving sessions by raw token
    """

    @staticmethod
    @transaction.atomic
    def start_session(
        *,
        user,
        website,
        ip: str | None = None,
        user_agent: str | None = None,
        device_info: dict[str, Any] | None = None,
        session_type: str = LoginSession.SessionType.PASSWORD,
        fingerprint_hash: str | None = None,
    ) -> tuple[LoginSession, str]:
        """
        Create a new login session.

        Args:
            user: User instance.
            website: Website instance.
            ip: Optional IP address.
            user_agent: Optional user agent string.
            device_info: Optional device metadata dictionary.
            session_type: Session type value.
            fingerprint_hash: Optional associated fingerprint hash.

        Returns:
            Tuple of:
                - created LoginSession instance
                - raw session token

        Raises:
            ValueError: If website is missing.
            ValidationError: If session_type is invalid.
        """
        if website is None:
            raise ValueError(
                "Website context is required to create a login session."
            )

        valid_session_types = {
            choice[0] for choice in LoginSession.SessionType.choices
        }
        if session_type not in valid_session_types:
            raise ValidationError("Invalid session type.")

        raw_token, token_hash = TokenService.generate_hashed_token()

        device_name = None
        if device_info:
            device_name = (
                device_info.get("device_name")
                or device_info.get("device")
            )

        max_age_seconds = getattr(
            settings,
            "SESSION_COOKIE_AGE",
            1209600,
        )
        expires_at = now() + timedelta(seconds=max_age_seconds)

        session = LoginSession.objects.create(
            user=user,
            website=website,
            token_hash=token_hash,
            session_type=session_type,
            ip_address=ip,
            user_agent=user_agent,
            device_name=device_name,
            fingerprint_hash=fingerprint_hash,
            logged_in_at=now(),
            last_activity_at=now(),
            expires_at=expires_at,
        )

        return session, raw_token

    @staticmethod
    def get_session_by_token(
        *,
        raw_token: str,
    ) -> LoginSession | None:
        """
        Retrieve a session by raw session token.

        Args:
            raw_token: Raw session token.

        Returns:
            Matching LoginSession instance or None.
        """
        token_hash = TokenService.hash_value(raw_token)

        session = LoginSession.objects.filter(
            token_hash=token_hash,
            revoked_at__isnull=True,
        ).first()

        if session is None:
            return None

        if not session.is_active:
            return None
        
        return session
    
    @staticmethod
    def get_idle_timeout_seconds(
        *,
        session: LoginSession,
    ) -> int:
        default_timeout = getattr(
            settings,
            "SESSION_IDLE_TIMEOUT",
            30 * 60,
        )

        if session.session_type == LoginSession.SessionType.IMPERSONATION:
            return getattr(
                settings,
                "IMPERSONATION_SESSION_IDLE_TIMEOUT",
                15 * 60,
            )

        return default_timeout
    @staticmethod
    def is_session_idle_expired(
        *,
        session: LoginSession,
    ) -> bool:
        timeout_seconds = LoginSessionService.get_idle_timeout_seconds(
            session=session,
        )

        reference_time = session.last_activity_at or session.logged_in_at
        if reference_time is None:
            return False

        return timezone.now() >= (
            reference_time + timedelta(seconds=timeout_seconds)
        )
    
    @staticmethod
    @transaction.atomic
    def revoke_if_expired(
        *,
        session: LoginSession,
        revoked_by=None,
    ) -> bool:
        if not session.is_active:
            return True

        if LoginSessionService.is_session_expired(session=session):
            session.revoke(revoked_by=revoked_by)
            return True

        if LoginSessionService.is_session_idle_expired(session=session):
            session.revoke(revoked_by=revoked_by)
            return True

        return False

    @staticmethod
    @transaction.atomic
    def revoke_session(
        *,
        user,
        session_id: str | int | None = None,
        website=None,
        revoked_by=None,
    ) -> bool:
        """
        Revoke a specific active session.

        Args:
            user: User instance.
            session_id: Session primary key to revoke.
            website: Optional website instance filter.
            revoked_by: Optional actor revoking the session.

        Returns:
            True if a session was revoked, otherwise False.
        """
        queryset = LoginSession.objects.filter(
            user=user,
            revoked_at__isnull=True,
        )

        if session_id is not None:
            queryset = queryset.filter(pk=session_id)

        if website is not None:
            queryset = queryset.filter(website=website)

        session = queryset.order_by("-logged_in_at").first()

        if session is None or not session.is_active:
            return False

        session.revoke(revoked_by=revoked_by)
        return True

    @staticmethod
    @transaction.atomic
    def revoke_all_sessions(
        *,
        user,
        website=None,
        exclude_session_id: str | int | None = None,
        revoked_by=None,
    ) -> int:
        """
        Revoke all active sessions for a user.

        Args:
            user: User instance.
            website: Optional website instance filter.
            exclude_session_id: Optional session ID to keep active.
            revoked_by: Optional actor revoking the sessions.

        Returns:
            Number of revoked sessions.
        """

        queryset = LoginSession.objects.filter(
            user=user,
            revoked_at__isnull=True,
        )

        if website is not None:
            queryset = queryset.filter(website=website)

        if exclude_session_id is not None:
            queryset = queryset.exclude(pk=exclude_session_id)

        active_qs = queryset.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now())
        )

        return active_qs.update(
            revoked_at=now(),
            revoked_by=revoked_by,
    )

    @staticmethod
    @transaction.atomic
    def touch_session(
        *,
        session: LoginSession,
    ) -> LoginSession:
        """
        Update last-activity timestamp for a session.

        Args:
            session: LoginSession instance.

        Returns:
            Updated LoginSession instance.
        """
        session.touch()
        return session

    @staticmethod
    def get_active_sessions(
        *,
        user,
        website=None,
    ) -> list[LoginSession]:
        """
        Retrieve currently active sessions for a user.

        Args:
            user: User instance.
            website: Optional website instance filter.

        Returns:
            List of active LoginSession instances.
        """
        queryset = LoginSession.objects.filter(
            user=user,
            revoked_at__isnull=True,
        ).order_by("-logged_in_at")

        if website is not None:
            queryset = queryset.filter(website=website)

        queryset = queryset.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now())
        )

        return list(queryset)
    

    @staticmethod
    def get_active_session_by_token_hash(
        *,
        token_hash: str,
        website=None,
    ) -> LoginSession | None:
        """
        Return an active session by token hash.
        """
        queryset = LoginSession.objects.filter(
            token_hash=token_hash,
            revoked_at__isnull=True,
        )

        if website is not None:
            queryset = queryset.filter(website=website)

        session = queryset.first()
    
        if session is None or not session.is_active:
            return None
        
        return session

    @staticmethod
    def is_session_expired(
        *,
        session: LoginSession,
    ) -> bool:
        """
        Check whether a session is expired using absolute expiry.
        """
        if session.expires_at is None:
            return False

        return timezone.now() >= session.expires_at
    

    @staticmethod
    def get_session_by_id(
        *,
        session_id: int,
        user,
        website=None,
    ) -> LoginSession | None:
        queryset = LoginSession.objects.filter(
            pk=session_id,
            user=user,
            revoked_at__isnull=True,
        )

        if website is not None:
            queryset = queryset.filter(website=website)

        session = queryset.first()

        if session is None or not session.is_active:
            return None

        return session
    

    @staticmethod
    def get_current_session_from_request(
        *,
        request,
    ) -> LoginSession | None:
        """
        Return the current LoginSession attached by middleware.
        """
        return getattr(request, "_login_session", None)

    @staticmethod
    def get_idle_remaining_seconds(
        *,
        session: LoginSession,
    ) -> int:
        """
        Return remaining idle time in seconds for a session.
        """
        timeout_seconds = LoginSessionService.get_idle_timeout_seconds(
            session=session,
        )

        reference_time = session.last_activity_at or session.logged_in_at
        if reference_time is None:
            return timeout_seconds

        elapsed = (timezone.now() - reference_time).total_seconds()
        remaining = max(int(timeout_seconds - elapsed), 0)
        return remaining