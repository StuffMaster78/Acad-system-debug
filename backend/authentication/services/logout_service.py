from django.core.exceptions import ValidationError

from authentication.models.security_events import SecurityEvent
from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.security_event_service import (
    SecurityEventService,
)


class LogoutService:
    """
    Handle logout flows for current session and all other sessions.
    """

    @staticmethod
    def logout_current_session(
        *,
        request,
    ) -> bool:
        """
        Revoke the current authenticated session.

        Returns:
            True if session was revoked, False otherwise.
        """
        user = getattr(request, "user", None)
        website = getattr(request, "website", None)
        session = getattr(request, "_login_session", None)

        if user is None or not user.is_authenticated:
            raise ValidationError("Authenticated user is required.")

        if website is None:
            raise ValidationError("Website context is required.")

        if session is None:
            raise ValidationError("Current session could not be resolved.")

        success = LoginSessionService.revoke_session(
            user=user,
            session_id=session.pk,
            website=website,
            revoked_by=user,
        )

        if success:
            SecurityEventService.log(
                user=user,
                website=website,
                event_type=SecurityEvent.EventType.LOGOUT,
                severity=SecurityEvent.Severity.LOW,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.headers.get("User-Agent", ""),
                device=getattr(session, "device_name", None),
                metadata={
                    "session_id": session.pk,
                    "logout_scope": "current_session",
                },
            )

        return success

    @staticmethod
    def logout_all_other_sessions(
        *,
        request,
    ) -> int:
        """
        Revoke all other sessions except the current one.

        Returns:
            Number of revoked sessions.
        """
        user = getattr(request, "user", None)
        website = getattr(request, "website", None)
        session = getattr(request, "_login_session", None)

        if user is None or not user.is_authenticated:
            raise ValidationError("Authenticated user is required.")

        if website is None:
            raise ValidationError("Website context is required.")

        if session is None:
            raise ValidationError("Current session could not be resolved.")

        revoked_count = LoginSessionService.revoke_all_sessions(
            user=user,
            website=website,
            exclude_session_id=session.pk,
            revoked_by=user,
        )

        SecurityEventService.log(
            user=user,
            website=website,
            event_type=SecurityEvent.EventType.LOGOUT,
            severity=SecurityEvent.Severity.LOW,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.headers.get("User-Agent", ""),
            device=getattr(session, "device_name", None),
            metadata={
                "session_id": session.pk,
                "logout_scope": "all_other_sessions",
                "revoked_sessions_count": revoked_count,
            },
        )

        return revoked_count