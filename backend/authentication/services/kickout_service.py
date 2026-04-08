from django.db import transaction

from authentication.models.login_session import LoginSession
from authentication.models.security_events import SecurityEvent
from authentication.services.security_event_service import (
    SecurityEventService,
)


class KickoutService:
    """
    Handle admin-initiated session termination for a user.
    """

    def __init__(self, website):
        """
        Initialize the kickout service.

        Args:
            website: Website instance.

        Raises:
            ValueError: If website is not provided.
        """
        if website is None:
            raise ValueError("Website context is required.")

        self.website = website

    @transaction.atomic
    def kick_user(
        self,
        *,
        user,
        performed_by,
        ip_address: str | None = None,
        reason: str = "",
    ) -> int:
        """
        Revoke active sessions for a user on the current website.

        Args:
            user: User whose sessions should be revoked.
            performed_by: Admin or staff user performing the action.
            ip_address: Optional IP filter to revoke only sessions from
                a specific IP.
            reason: Optional reason for revocation.

        Returns:
            Number of revoked sessions.
        """
        queryset = LoginSession.objects.filter(
            user=user,
            website=self.website,
            revoked_at__isnull=True,
        )

        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)

        sessions = list(queryset.order_by("-logged_in_at"))

        revoked_count = 0

        for session in sessions:
            if not session.is_active:
                continue

            session.revoke(revoked_by=performed_by)
            revoked_count += 1

            SecurityEventService.log(
                user=user,
                website=self.website,
                event_type=SecurityEvent.EventType.SESSION_REVOKED,
                severity=SecurityEvent.Severity.MEDIUM,
                is_suspicious=False,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                device=session.device_name,
                metadata={
                    "reason": reason or "admin_kick",
                    "performed_by_user_id": getattr(
                        performed_by,
                        "pk",
                        None,
                    ),
                    "session_id": session.pk,
                    "session_type": session.session_type,
                },
            )

        return revoked_count