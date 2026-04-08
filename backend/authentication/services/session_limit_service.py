"""
Session limit service.

Manage concurrent session limits and enforcement for a user on a
website.
"""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils.timezone import now

from authentication.models.login_session import LoginSession
from authentication.models.session_limits import SessionLimitPolicy
from authentication.models.security_events import SecurityEvent
from authentication.services.security_event_service import (
    SecurityEventService,
)
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService
)


class SessionLimitService:
    """
    Manage concurrent session limit policy and enforcement.
    """

    DEFAULT_MAX_SESSIONS = 3

    def __init__(self, user, website):
        """
        Initialize the session limit service.

        Args:
            user: User instance.
            website: Website instance.

        Raises:
            ValueError: If website is not provided.
        """
        if website is None:
            raise ValueError(
                "Website context is required for session limits."
            )

        self.user = user
        self.website = website

    def get_or_create_policy(self) -> SessionLimitPolicy:
        """
        Get or create the user's session limit policy.

        Returns:
            SessionLimitPolicy instance.
        """
        AccountAccessPolicyService.validate_auth_access(
            user=self.user,
            website=self.website,
        )
        policy, _ = SessionLimitPolicy.objects.get_or_create(
            user=self.user,
            website=self.website,
            defaults={
                "max_concurrent_sessions": self.DEFAULT_MAX_SESSIONS,
                "allow_unlimited_trusted": False,
                "revoke_oldest_on_limit": True,
            },
        )
        return policy

    def get_active_sessions(self) -> list[LoginSession]:
        """
        Get currently active sessions for the user.

        Returns:
            List of active LoginSession records ordered oldest first.
        """
        queryset = LoginSession.objects.filter(
            user=self.user,
            website=self.website,
            revoked_at__isnull=True,
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now())
        ).order_by("logged_in_at")

        return list(queryset)

    def get_active_session_count(self) -> int:
        """
        Get the number of active sessions.

        Returns:
            Number of active sessions.
        """
        return len(self.get_active_sessions())

    @transaction.atomic
    def enforce_session_limit(
        self,
        *,
        new_session: LoginSession | None = None,
        is_trusted_device: bool = False,
    ) -> LoginSession | None:
        """
        Enforce the user's concurrent session limit.

        Args:
            new_session: Optional newly created session.
            is_trusted_device: Whether the current device is trusted.

        Returns:
            Revoked LoginSession if one was revoked, otherwise None.

        Raises:
            ValidationError: If session limit is exceeded and policy
                forbids auto-revocation.
        """
        policy = self.get_or_create_policy()

        if (
            policy.allow_unlimited_trusted
            and is_trusted_device
        ):
            return None

        active_sessions = self.get_active_sessions()
        max_sessions = policy.max_concurrent_sessions

        if len(active_sessions) < max_sessions:
            return None

        if not policy.revoke_oldest_on_limit:
            raise ValidationError(
                f"Maximum number of concurrent sessions "
                f"({max_sessions}) reached."
            )

        oldest_session = active_sessions[0]

        if (
            new_session is not None
            and oldest_session.pk == new_session.pk
            and len(active_sessions) == 1
        ):
            return None

        oldest_session.revoke()

        SecurityEventService.log(
            user=self.user,
            website=self.website,
            event_type=SecurityEvent.EventType.SESSION_REVOKED,
            severity=SecurityEvent.Severity.LOW,
            metadata={
                "reason": "session_limit_reached",
                "max_sessions": max_sessions,
                "revoked_session_id": oldest_session.pk,
                "new_session_id": new_session.pk if new_session else None,
            },
        )

        return oldest_session

    @transaction.atomic
    def validate_can_start_session(
        self,
        *,
        is_trusted_device: bool = False,
    ) -> None:
        """
        Validate whether a new session may be started without creating
        it yet.

        Args:
            is_trusted_device: Whether the current device is trusted.

        Raises:
            ValidationError: If a new session cannot be started.
        """
        policy = self.get_or_create_policy()

        if (
            policy.allow_unlimited_trusted
            and is_trusted_device
        ):
            return

        active_count = self.get_active_session_count()

        if (
            active_count >= policy.max_concurrent_sessions
            and not policy.revoke_oldest_on_limit
        ):
            raise ValidationError(
                f"Maximum number of concurrent sessions "
                f"({policy.max_concurrent_sessions}) reached."
            )

    @transaction.atomic
    def update_policy(
        self,
        *,
        max_concurrent_sessions: int | None = None,
        allow_unlimited_trusted: bool | None = None,
        revoke_oldest_on_limit: bool | None = None,
    ) -> SessionLimitPolicy:
        """
        Update the user's session limit policy.

        Args:
            max_concurrent_sessions: New max concurrent session count.
            allow_unlimited_trusted: Whether trusted devices bypass
                session limits.
            revoke_oldest_on_limit: Whether to revoke the oldest session
                automatically when the limit is reached.

        Returns:
            Updated SessionLimitPolicy instance.
        """
        policy = self.get_or_create_policy()

        if max_concurrent_sessions is not None:
            policy.max_concurrent_sessions = max_concurrent_sessions

        if allow_unlimited_trusted is not None:
            policy.allow_unlimited_trusted = allow_unlimited_trusted

        if revoke_oldest_on_limit is not None:
            policy.revoke_oldest_on_limit = revoke_oldest_on_limit

        policy.full_clean()
        policy.save()

        return policy

    def get_session_limit_info(self) -> dict:
        """
        Get current session-limit information for the user.

        Returns:
            Dictionary of current policy and active-session counts.
        """
        policy = self.get_or_create_policy()
        active_count = self.get_active_session_count()

        return {
            "max_concurrent_sessions": policy.max_concurrent_sessions,
            "active_sessions": active_count,
            "remaining_sessions": max(
                0,
                policy.max_concurrent_sessions - active_count,
            ),
            "allow_unlimited_trusted": (
                policy.allow_unlimited_trusted
            ),
            "revoke_oldest_on_limit": (
                policy.revoke_oldest_on_limit
            ),
        }