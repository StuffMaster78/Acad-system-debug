from django.core.exceptions import ValidationError
from django.utils import timezone

from authentication.models.account_lockout import AccountLockout
from authentication.models.failed_login_attempts import FailedLoginAttempt
from authentication.models.security_events import SecurityEvent
from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.security_event_service import (
    SecurityEventService,
)


class LockoutAdminService:
    """
    Admin/support actions for lockout and forced session revocation.
    """

    @staticmethod
    def unlock_user(
        *,
        target_user,
        website,
        performed_by,
    ) -> int:
        """
        Clear active lockouts and failed login attempts for a user.

        Returns:
            Number of active lockouts cleared.
        """
        if website is None:
            raise ValidationError("Website context is required.")

        if target_user is None:
            raise ValidationError("Target user is required.")

        updated_count = AccountLockout.objects.filter(
            user=target_user,
            website=website,
            is_active=True,
        ).update(
            is_active=False,
            unlocked_at=timezone.now(),
        )

        FailedLoginAttempt.objects.filter(
            user=target_user,
            website=website,
        ).delete()

        SecurityEventService.log(
            user=target_user,
            website=website,
            event_type=SecurityEvent.EventType.ACCOUNT_UNLOCKED,
            severity=SecurityEvent.Severity.MEDIUM,
            metadata={
                "performed_by_user_id": getattr(performed_by, "pk", None),
                "unlock_scope": "admin_unlock",
            },
        )

        return updated_count

    @staticmethod
    def kickout_user(
        *,
        target_user,
        website,
        performed_by,
        reason: str = "",
    ) -> int:
        """
        Revoke all active sessions for a target user.

        Returns:
            Number of revoked sessions.
        """
        if website is None:
            raise ValidationError("Website context is required.")

        if target_user is None:
            raise ValidationError("Target user is required.")

        revoked_count = LoginSessionService.revoke_all_sessions(
            user=target_user,
            website=website,
            revoked_by=performed_by,
        )

        SecurityEventService.log(
            user=target_user,
            website=website,
            event_type=SecurityEvent.EventType.SESSION_REVOKED,
            severity=SecurityEvent.Severity.MEDIUM,
            metadata={
                "performed_by_user_id": getattr(performed_by, "pk", None),
                "revoked_sessions_count": revoked_count,
                "reason": reason,
                "revocation_scope": "admin_kickout",
            },
        )

        return revoked_count