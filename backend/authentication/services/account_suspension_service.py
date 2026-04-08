"""
Account suspension service.

Handle website-scoped account suspension workflows such as suspension,
reactivation, scheduled reactivation checks, and active-session
revocation.
"""

import logging
from typing import Any

from django.db import transaction
from django.utils import timezone

from authentication.models.account_suspension import (
    AccountSuspension,
)
from authentication.models.login_session import LoginSession


logger = logging.getLogger(__name__)


class AccountSuspensionService:
    """
    Manage website-scoped account suspension workflows.
    """

    def __init__(self, user, website):
        """
        Initialize the account suspension service.

        Args:
            user: User instance.
            website: Website instance.

        Raises:
            ValueError: If website is not provided.
        """
        if website is None:
            raise ValueError(
                "Website context is required for account suspension."
            )

        self.user = user
        self.website = website

    def get_or_create_suspension(self) -> AccountSuspension:
        """
        Get or create the suspension record for the user and website.

        Returns:
            AccountSuspension instance.
        """
        suspension, _ = AccountSuspension.objects.get_or_create(
            user=self.user,
            website=self.website,
            defaults={
                "is_suspended": False,
            },
        )
        return suspension

    @transaction.atomic
    def suspend(
        self,
        *,
        reason: str = "",
        suspension_type: str = (
            AccountSuspension.SuspensionType.USER_INITIATED
        ),
        scheduled_reactivation_at=None,
        revoke_sessions: bool = True,
    ) -> AccountSuspension:
        """
        Suspend the user's account for the current website.

        Args:
            reason: Reason for suspension.
            suspension_type: Suspension type value.
            scheduled_reactivation_at: Optional scheduled reactivation
                datetime.
            revoke_sessions: Whether to revoke active login sessions.

        Returns:
            Updated AccountSuspension instance.
        """
        suspension = self.get_or_create_suspension()

        suspension.is_suspended = True
        suspension.suspension_reason = reason
        suspension.suspension_type = suspension_type
        suspension.suspended_at = timezone.now()
        suspension.scheduled_reactivation_at = (
            scheduled_reactivation_at
        )
        suspension.reactivated_at = None
        suspension.save(
            update_fields=[
                "is_suspended",
                "reason",
                "suspension_type",
                "suspended_at",
                "scheduled_reactivation_at",
                "reactivated_at",
            ],
        )

        if revoke_sessions:
            self.revoke_all_sessions()

        self._log_security_event(
            event_type="account_suspended",
            severity="medium",
            metadata={
                "reason": reason,
                "scheduled_reactivation_at": (
                    scheduled_reactivation_at.isoformat()
                    if scheduled_reactivation_at
                    else None
                ),
                "suspension_type": suspension_type,
            },
        )

        return suspension

    @transaction.atomic
    def reactivate(self) -> AccountSuspension:
        """
        Reactivate the user's account for the current website.

        Returns:
            Updated AccountSuspension instance.
        """
        suspension = self.get_or_create_suspension()

        suspension.is_suspended = False
        suspension.reactivated_at = timezone.now()
        suspension.save(
            update_fields=["is_suspended", "reactivated_at"],
        )

        self._log_security_event(
            event_type="account_reactivated",
            severity="low",
            metadata={
                "user_initiated": True,
            },
        )

        return suspension

    def is_suspended(self) -> bool:
        """
        Determine whether the user's account is currently suspended.

        Returns:
            True if suspended, otherwise False.
        """
        suspension = self.get_or_create_suspension()

        if (
            suspension.is_suspended
            and suspension.scheduled_reactivation_at
            and timezone.now() >= suspension.scheduled_reactivation_at
        ):
            self.reactivate()
            suspension.refresh_from_db()

        return bool(suspension.is_suspended)

    @transaction.atomic
    def check_scheduled_reactivation(self) -> bool:
        """
        Check whether scheduled reactivation should occur now.

        Returns:
            True if reactivation occurred, otherwise False.
        """
        suspension = self.get_or_create_suspension()

        if (
            suspension.is_suspended
            and suspension.scheduled_reactivation_at
            and timezone.now() >= suspension.scheduled_reactivation_at
        ):
            self.reactivate()
            logger.info(
                "Account %s automatically reactivated on website %s",
                getattr(self.user, "email", self.user.pk),
                getattr(self.website, "pk", None),
            )
            return True

        return False

    def revoke_all_sessions(self) -> int:
        """
        Revoke all active login sessions for the user on the website.

        Returns:
            Number of revoked sessions.
        """
        active_sessions = LoginSession.objects.filter(
            user=self.user,
            website=self.website,
            is_active=True,
        )

        count = 0
        for session in active_sessions:
            session.revoke()
            count += 1

        return count

    def get_suspension_info(self) -> dict[str, Any]:
        """
        Return suspension details for the user and website.

        Returns:
            Dictionary of suspension information.
        """
        suspension = self.get_or_create_suspension()

        return {
            "is_suspended": suspension.is_suspended,
            "suspended_at": (
                suspension.suspended_at.isoformat()
                if suspension.suspended_at
                else None
            ),
            "reason": suspension.suspension_reason,
            "suspension_type": suspension.suspension_type,
            "scheduled_reactivation_at": (
                suspension.scheduled_reactivation_at.isoformat()
                if suspension.scheduled_reactivation_at
                else None
            ),
            "reactivated_at": (
                suspension.reactivated_at.isoformat()
                if suspension.reactivated_at
                else None
            ),
        }

    def _log_security_event(
        self,
        *,
        event_type: str,
        severity: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Best-effort security event logging.

        Args:
            event_type: Security event type.
            severity: Security event severity.
            metadata: Optional event metadata.
        """
        try:
            from authentication.models.security_events import SecurityEvent

            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type=event_type,
                severity=severity,
                is_suspicious=False,
                metadata=metadata or {},
            )
        except Exception as exc:
            logger.warning(
                "Failed to log security event for user=%s website=%s: %s",
                getattr(self.user, "pk", None),
                getattr(self.website, "pk", None),
                exc,
            )