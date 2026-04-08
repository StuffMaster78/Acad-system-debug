"""
Password expiration service.

Manage password expiration policy and status for a user on a website.
"""

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from authentication.models.password_security import (
    PasswordExpirationPolicy,
)


class PasswordExpirationService:
    """
    Manage password expiration policy for a user on a website.
    """

    DEFAULT_EXPIRATION_DAYS = 90
    DEFAULT_WARNING_DAYS = 7

    def __init__(self, user, website):
        """
        Initialize the password expiration service.

        Args:
            user: User instance.
            website: Website instance.

        Raises:
            ValueError: If website is not provided.
        """
        if website is None:
            raise ValueError(
                "Website context is required for password expiration."
            )

        self.user = user
        self.website = website

    def get_or_create_policy(self) -> PasswordExpirationPolicy:
        """
        Get or create password expiration policy for user and website.

        Returns:
            PasswordExpirationPolicy instance.
        """
        policy, _ = PasswordExpirationPolicy.objects.get_or_create(
            user=self.user,
            website=self.website,
            defaults={
                "password_changed_at": timezone.now(),
                "expires_in_days": self.DEFAULT_EXPIRATION_DAYS,
                "warning_days_before": self.DEFAULT_WARNING_DAYS,
            },
        )
        return policy

    @transaction.atomic
    def update_password_changed(self) -> PasswordExpirationPolicy:
        """
        Update policy after password change.

        Returns:
            Updated PasswordExpirationPolicy instance.
        """
        policy = self.get_or_create_policy()
        policy.password_changed_at = timezone.now()
        policy.last_warning_sent = None
        policy.save(
            update_fields=[
                "password_changed_at",
                "last_warning_sent",
            ]
        )
        return policy

    def get_expiration_status(self) -> dict:
        """
        Compute password expiration status.

        Returns:
            Dictionary containing expiration details.
        """
        policy = self.get_or_create_policy()

        if policy.is_exempt:
            return {
                "is_exempt": True,
                "is_expired": False,
                "is_expiring_soon": False,
                "days_until_expiration": None,
                "expires_at": None,
                "password_changed_at": (
                    policy.password_changed_at.isoformat()
                ),
            }

        expires_at = (
            policy.password_changed_at
            + timezone.timedelta(days=policy.expires_in_days)
        )
        is_expired = timezone.now() >= expires_at

        if is_expired:
            days_until_expiration = 0
            is_expiring_soon = False
        else:
            delta = expires_at - timezone.now()
            days_until_expiration = max(0, delta.days)
            warning_at = expires_at - timezone.timedelta(
                days=policy.warning_days_before
            )
            is_expiring_soon = timezone.now() >= warning_at

        return {
            "is_exempt": False,
            "is_expired": is_expired,
            "is_expiring_soon": is_expiring_soon,
            "days_until_expiration": days_until_expiration,
            "expires_at": expires_at.isoformat(),
            "password_changed_at": (
                policy.password_changed_at.isoformat()
            ),
        }

    def require_password_change(self) -> bool:
        """
        Determine whether password change is required.

        Returns:
            True if password is expired, otherwise False.
        """
        status = self.get_expiration_status()
        return bool(status["is_expired"])

    def should_send_warning(self) -> bool:
        """
        Determine whether an expiration warning should be sent.

        Returns:
            True if warning should be sent, otherwise False.
        """
        policy = self.get_or_create_policy()
        status = self.get_expiration_status()

        if policy.is_exempt or status["is_expired"]:
            return False

        if not status["is_expiring_soon"]:
            return False

        if policy.last_warning_sent:
            if timezone.now() - policy.last_warning_sent < timedelta(
                hours=24,
            ):
                return False

        return True

    @transaction.atomic
    def mark_warning_sent(self) -> PasswordExpirationPolicy:
        """
        Mark that an expiration warning has been sent.

        Returns:
            Updated PasswordExpirationPolicy instance.
        """
        policy = self.get_or_create_policy()
        policy.last_warning_sent = timezone.now()
        policy.save(update_fields=["last_warning_sent"])
        return policy

    @transaction.atomic
    def set_exemption(
        self,
        *,
        is_exempt: bool,
        reason: str = "",
    ) -> PasswordExpirationPolicy:
        """
        Set password expiration exemption.

        Args:
            is_exempt: Whether user is exempt.
            reason: Optional audit reason.

        Returns:
            Updated PasswordExpirationPolicy instance.
        """
        policy = self.get_or_create_policy()
        policy.is_exempt = is_exempt
        policy.save(update_fields=["is_exempt"])

        self._log_security_event(
            event_type="password_expiration_exemption_changed",
            severity="low",
            metadata={
                "is_exempt": is_exempt,
                "reason": reason,
            },
        )

        return policy

    @transaction.atomic
    def update_policy(
        self,
        *,
        expires_in_days: int | None = None,
        warning_days_before: int | None = None,
    ) -> PasswordExpirationPolicy:
        """
        Update expiration policy values.

        Args:
            expires_in_days: Password lifetime in days.
            warning_days_before: Warning lead time in days.

        Returns:
            Updated PasswordExpirationPolicy instance.
        """
        policy = self.get_or_create_policy()

        if expires_in_days is not None:
            policy.expires_in_days = expires_in_days

        if warning_days_before is not None:
            policy.warning_days_before = warning_days_before

        policy.save(
            update_fields=[
                "expires_in_days",
                "warning_days_before",
            ]
        )

        return policy

    def _log_security_event(
        self,
        *,
        event_type: str,
        severity: str,
        metadata: dict | None = None,
    ) -> None:
        """
        Best-effort security event logging.

        Args:
            event_type: Event type.
            severity: Event severity.
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
        except Exception:
            pass