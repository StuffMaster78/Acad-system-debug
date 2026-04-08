from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from authentication.models.failed_login_attempts import (
    FailedLoginAttempt,
)


@dataclass(frozen=True)
class LockoutDecision:
    """
    Represent the result of a lockout policy evaluation.
    """

    should_lock: bool
    reason: str | None
    duration_minutes: int
    failed_attempts: int
    attempts_remaining: int


class LockoutPolicyService:
    """
    Evaluate adaptive lockout policy based on recent failed login
    attempts, IP patterns, trusted device status, and recent login
    history.

    This service does not enforce lockouts directly. It only returns
    policy decisions. Enforcement belongs in LoginSecurityService.
    """

    DEFAULT_WINDOW_MINUTES = 15
    DEFAULT_BASE_DURATION_MINUTES = 5

    def __init__(self, user, website):
        """
        Initialize the lockout policy service.

        Args:
            user: User instance.
            website: Website instance.
        """
        self.user = user
        self.website = website

    def evaluate(
        self,
        *,
        ip_address: str | None,
        is_trusted_device: bool = False,
    ) -> LockoutDecision:
        """
        Evaluate whether the user should be locked out.

        Args:
            ip_address: Source IP address.
            is_trusted_device: Whether the current device is trusted.

        Returns:
            LockoutDecision containing the policy result.
        """
        failed_attempts = self._get_recent_failed_attempts_count()

        if is_trusted_device:
            threshold = 10
            reason = "Too many failed attempts on trusted device"
        elif ip_address and self._is_same_ip_as_recent_attempts(
            ip_address=ip_address,
        ):
            threshold = 3
            reason = "Multiple failed attempts from same location"
        elif self._has_recent_successful_login(hours=24):
            threshold = 7
            reason = (
                "Multiple failed attempts after recent successful login"
            )
        else:
            threshold = 5
            reason = "Too many failed login attempts"

        should_lock = failed_attempts >= threshold
        attempts_remaining = max(0, threshold - failed_attempts)

        duration_minutes = 0
        if should_lock:
            duration_minutes = self.get_lockout_duration(
                ip_address=ip_address,
                is_trusted_device=is_trusted_device,
            )

        return LockoutDecision(
            should_lock=should_lock,
            reason=reason if should_lock else None,
            duration_minutes=duration_minutes,
            failed_attempts=failed_attempts,
            attempts_remaining=attempts_remaining,
        )

    def get_lockout_duration(
        self,
        *,
        ip_address: str | None,
        is_trusted_device: bool = False,
    ) -> int:
        """
        Calculate lockout duration in minutes.

        Args:
            ip_address: Source IP address.
            is_trusted_device: Whether the current device is trusted.

        Returns:
            Lockout duration in minutes.
        """
        base_duration = self.DEFAULT_BASE_DURATION_MINUTES
        failed_attempts = self._get_recent_failed_attempts_count()

        if (
            ip_address
            and self._is_same_ip_as_recent_attempts(
                ip_address=ip_address,
            )
        ):
            return base_duration * (2 + (failed_attempts // 3))

        if is_trusted_device:
            return base_duration

        if self._has_recent_successful_login(hours=24):
            return base_duration

        return base_duration * (1 + (failed_attempts // 3))

    def _get_recent_failed_attempts_count(
        self,
        *,
        minutes: int = DEFAULT_WINDOW_MINUTES,
    ) -> int:
        """
        Count recent failed login attempts.

        Args:
            minutes: Lookback window in minutes.

        Returns:
            Number of recent failed login attempts.
        """
        cutoff = timezone.now() - timedelta(minutes=minutes)

        return FailedLoginAttempt.objects.filter(
            user=self.user,
            website=self.website,
            timestamp__gte=cutoff,
        ).count()

    def _is_same_ip_as_recent_attempts(
        self,
        *,
        ip_address: str,
    ) -> bool:
        """
        Check whether the same IP has been used in recent failures.

        Args:
            ip_address: Source IP address.

        Returns:
            True if the same IP appears in at least two recent failed
            attempts, otherwise False.
        """
        cutoff = timezone.now() - timedelta(minutes=15)

        recent_attempts = FailedLoginAttempt.objects.filter(
            user=self.user,
            website=self.website,
            timestamp__gte=cutoff,
            ip_address=ip_address,
        ).count()

        return recent_attempts >= 2

    def _has_recent_successful_login(
        self,
        *,
        hours: int = 24,
    ) -> bool:
        """
        Check whether the user logged in successfully recently.

        Args:
            hours: Lookback window in hours.

        Returns:
            True if the user has a recent successful login, otherwise
            False.
        """
        last_login = getattr(self.user, "last_login", None)
        if not last_login:
            return False

        cutoff = timezone.now() - timedelta(hours=hours)
        return last_login >= cutoff