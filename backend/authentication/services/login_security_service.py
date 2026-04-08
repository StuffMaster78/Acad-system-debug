from datetime import timedelta
from typing import Any
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from authentication.models.account_lockout import (
    AccountLockout
)
from authentication.models.blocked_ip import BlockedIP
from authentication.models.blocked_ip_log import BlockedIPLog
from authentication.models.failed_login_attempts import (
    FailedLoginAttempt,
)

from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService,
)
from authentication.services.lockout_policy_service import (
    LockoutPolicyService,
)
from authentication.services.security_alert_service import (
    SecurityAlertService,
)


User = get_user_model()


class LoginSecurityService:
    """
    Handle login security concerns such as failed-login tracking,
    lockout enforcement, IP blocking, and lockout cleanup.
    """

    DEFAULT_WINDOW_MINUTES = 15
    DEFAULT_MAX_ATTEMPTS = 5
    DEFAULT_IP_BLOCK_MINUTES = 30

    @staticmethod
    def get_user_by_email(*, email: str):
        """
        Retrieve a user by email address.

        Args:
            email: User email address.

        Returns:
            User instance or None.
        """
        return User.objects.filter(email=email).first()

    @staticmethod
    def get_failed_attempt_count(
        *,
        user,
        website,
        window_minutes: int,
    ) -> int:
        """
        Count recent failed login attempts for a user within a time
        window.

        Args:
            user: User instance.
            website: Website instance.
            window_minutes: Time window in minutes.

        Returns:
            Number of recent failed login attempts.
        """
        threshold = timezone.now() - timedelta(
            minutes=window_minutes,
        )

        return FailedLoginAttempt.objects.filter(
            user=user,
            website=website,
            timestamp__gte=threshold,
        ).count()

    @staticmethod
    def is_ip_blocked(
        *,
        website,
        ip_address: str | None,
    ) -> bool:
        """
        Determine whether an IP address is currently blocked for a
        website.

        Args:
            website: Website instance.
            ip_address: IP address to check.

        Returns:
            True if the IP is actively blocked, otherwise False.
        """
        if not ip_address:
            return False

        blocked_ip = BlockedIP.objects.filter(
            website=website,
            ip_address=ip_address,
        ).first()

        if blocked_ip is None:
            return False

        if not blocked_ip.is_active:
            blocked_ip.delete()
            return False

        return True

    @classmethod
    def is_locked_out(
        cls,
        *,
        user,
        website,
        window_minutes: int | None = None,
        max_attempts: int | None = None,
    ) -> bool:
        """
        Determine whether a user is currently locked out based on
        failed login attempts.

        Args:
            user: User instance.
            website: Website instance.
            window_minutes: Optional lockout window override.
            max_attempts: Optional max-attempts override.

        Returns:
            True if locked out, otherwise False.
        """
        effective_window = window_minutes or cls.DEFAULT_WINDOW_MINUTES
        effective_max_attempts = (
            max_attempts or cls.DEFAULT_MAX_ATTEMPTS
        )

        recent_attempts = cls.get_failed_attempt_count(
            user=user,
            website=website,
            window_minutes=effective_window,
        )

        return recent_attempts >= effective_max_attempts
    
    @staticmethod
    def get_active_lockout(
        *,
        user,
        website,
    ) -> AccountLockout | None:
        """
        Retrieve the user's current active lockout, if any.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            Active AccountLockout or None.
        """
        lockout = AccountLockout.objects.filter(
            user=user,
            website=website,
            is_active=True,
        ).order_by("-locked_at").first()

        if lockout is None:
            return None

        if not lockout.is_effective:
            lockout.clear()
            return None

        return lockout

    @staticmethod
    @transaction.atomic
    def create_account_lockout(
        *,
        user,
        website,
        reason: str,
        duration_minutes: int | None = None,
        lock_type: str = AccountLockout.LockType.AUTOMATIC,
        created_by=None,
    ) -> AccountLockout:
        """
        Create an account lockout.

        Args:
            user: User instance.
            website: Website instance.
            reason: Lockout reason.
            duration_minutes: Optional temporary lockout duration.
            lock_type: Lock type value.
            created_by: Optional admin who initiated the lockout.

        Returns:
            Created AccountLockout instance.
        """
        expires_at = None
        if duration_minutes and duration_minutes > 0:
            expires_at = timezone.now() + timedelta(
                minutes=duration_minutes,
            )

        return AccountLockout.objects.create(
            user=user,
            website=website,
            reason=reason,
            lock_type=lock_type,
            created_by=created_by,
            expires_at=expires_at,
        )

    @classmethod
    @transaction.atomic
    def record_failed_login(
        cls,
        *,
        user,
        website,
        ip_address: str | None = None,
        user_agent: str | None = None,
        city: str | None = None,
        region: str | None = None,
        country: str | None = None,
        asn: str | None = None,
        max_attempts: int | None = None,
        window_minutes: int | None = None,
        block_duration_minutes: int | None = None,
    ) -> FailedLoginAttempt:
        """
        Record a failed login attempt and optionally block the IP if the
        lockout threshold is reached.

        Args:
            user: User instance.
            website: Website instance.
            ip_address: Optional source IP address.
            user_agent: Optional source user agent.
            city: Optional city.
            region: Optional region.
            country: Optional country.
            asn: Optional ASN.
            max_attempts: Optional max-attempts override.
            window_minutes: Optional lockout window override.
            block_duration_minutes: Optional IP block duration override.

        Returns:
            Created FailedLoginAttempt instance.
        """
        attempt = FailedLoginAttempt.objects.create(
            user=user,
            website=website,
            ip_address=ip_address,
            user_agent=user_agent,
            city=city,
            region=region,
            country=country,
            asn=asn,
        )

        effective_max_attempts = (
            max_attempts or cls.DEFAULT_MAX_ATTEMPTS
        )
        effective_window = window_minutes or cls.DEFAULT_WINDOW_MINUTES
        effective_block_duration = (
            block_duration_minutes or cls.DEFAULT_IP_BLOCK_MINUTES
        )

        is_now_locked = cls.is_locked_out(
            user=user,
            website=website,
            window_minutes=effective_window,
            max_attempts=effective_max_attempts,
        )

        if is_now_locked and ip_address:
            cls.block_ip(
                website=website,
                ip_address=ip_address,
                duration_minutes=effective_block_duration,
                reason=(
                    "Too many failed login attempts within the "
                    "lockout window."
                ),
            )

        return attempt

    @staticmethod
    @transaction.atomic
    def block_ip(
        *,
        website,
        ip_address: str,
        duration_minutes: int,
        reason: str,
    ) -> BlockedIP:
        """
        Block an IP address for a website and record the block event.

        Args:
            website: Website instance.
            ip_address: IP address to block.
            duration_minutes: Block duration in minutes.
            reason: Reason for blocking the IP.

        Returns:
            BlockedIP instance.
        """
        blocked_until = timezone.now() + timedelta(
            minutes=duration_minutes,
        )

        blocked_ip, _ = BlockedIP.objects.update_or_create(
            website=website,
            ip_address=ip_address,
            defaults={
                "blocked_until": blocked_until,
            },
        )

        BlockedIPLog.objects.create(
            website=website,
            ip_address=ip_address,
            reason=reason,
            duration_minutes=duration_minutes,
        )

        SecurityAlertService.send_ip_block_alert(
            website=website,
            ip_address=ip_address,
            reason=reason,
            duration_minutes=duration_minutes,
        )

        return blocked_ip

    @staticmethod
    @transaction.atomic
    def unblock_ip(
        *,
        website,
        ip_address: str,
    ) -> int:
        """
        Remove an IP block for a website.

        Args:
            website: Website instance.
            ip_address: IP address to unblock.

        Returns:
            Number of deleted blocked IP records.
        """
        deleted_count, _ = BlockedIP.objects.filter(
            website=website,
            ip_address=ip_address,
        ).delete()

        return deleted_count

    @staticmethod
    def clear_expired_ip_blocks() -> int:
        """
        Delete expired IP block records.

        Returns:
            Number of deleted blocked IP records.
        """
        deleted_count, _ = BlockedIP.objects.filter(
            blocked_until__lte=timezone.now(),
        ).delete()

        return deleted_count
    
    @classmethod
    @transaction.atomic
    def record_failed_login_and_enforce(
        cls,
        *,
        user,
        website,
        ip_address: str | None = None,
        user_agent: str | None = None,
        city: str | None = None,
        region: str | None = None,
        country: str | None = None,
        asn: str | None = None,
        is_trusted_device: bool = False,
    ) -> dict[str, Any]:
        """
        Record a failed login, evaluate lockout policy, and enforce any
        required lockout or IP blocking.

        Args:
            user: User instance.
            website: Website instance.
            ip_address: Source IP address.
            user_agent: Source user agent.
            city: Optional city.
            region: Optional region.
            country: Optional country.
            asn: Optional ASN.
            is_trusted_device: Whether the request came from a trusted
                device.

        Returns:
            A dictionary describing the enforcement result.
        """
        attempt = FailedLoginAttempt.objects.create(
            user=user,
            website=website,
            ip_address=ip_address,
            user_agent=user_agent,
            city=city,
            region=region,
            country=country,
            asn=asn,
        )

        policy = LockoutPolicyService(user=user, website=website)
        decision = policy.evaluate(
            ip_address=ip_address,
            is_trusted_device=is_trusted_device,
        )

        lockout = None
        blocked_ip = None

        if decision.should_lock:
            lockout = cls.create_account_lockout(
                user=user,
                website=website,
                reason=decision.reason or "Too many failed logins.",
                duration_minutes=decision.duration_minutes,
                lock_type=AccountLockout.LockType.AUTOMATIC,
            )

            if ip_address:
                blocked_ip = cls.block_ip(
                    website=website,
                    ip_address=ip_address,
                    duration_minutes=max(
                        decision.duration_minutes,
                        cls.DEFAULT_IP_BLOCK_MINUTES,
                    ),
                    reason=decision.reason or "Too many failed logins.",
                )

            AuthNotificationBridgeService.send_account_lockout_notification(
                user=user,
                website=website,
                reason=decision.reason or "Too many failed logins.",
                duration_minutes=decision.duration_minutes,
            )

        return {
            "attempt": attempt,
            "decision": decision,
            "lockout": lockout,
            "blocked_ip": blocked_ip,
        }

    @staticmethod
    def clear_failed_logins(
        *,
        user,
        website,
    ) -> int:
        """
        Delete failed login attempts for a user after successful login.

        Args:
            user: User instance.
            website: Website instance.

        Returns:
            Number of deleted records.
        """
        deleted_count, _ = FailedLoginAttempt.objects.filter(
            user=user,
            website=website,
        ).delete()

        return deleted_count

    @staticmethod
    @transaction.atomic
    def clear_expired_lockouts() -> int:
        """
        Clear expired active account lockouts.

        Returns:
            Number of lockouts cleared.
        """
        lockouts = AccountLockout.objects.filter(
            is_active=True,
            expires_at__isnull=False,
            expires_at__lte=timezone.now(),
        )

        count = 0
        for lockout in lockouts:
            lockout.clear()
            count += 1

        return count
    
    @staticmethod
    def validate_login_allowed(
        *,
        user,
        website,
    ) -> None:
        """
        Validate that login is currently allowed for the user.

        Args:
            user: User instance.
            website: Website instance.

        Raises:
            ValidationError: If login is blocked by lockout or other
                security restrictions.
        """
        active_lockout = AccountLockout.objects.filter(
            user=user,
            website=website,
            active=True,
        ).first()

        if active_lockout is not None:
            raise ValidationError(
                "This account is temporarily locked."
            )

    @staticmethod
    def record_successful_login(
        *,
        user,
        website,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> int:
        """
        Clear recent failed-login records after successful login.

        Args:
            user: User instance.
            website: Website instance.
            ip_address: Optional source IP.
            user_agent: Optional source user agent.

        Returns:
            Number of deleted failed-attempt rows.
        """
        deleted_count, _ = FailedLoginAttempt.objects.filter(
            user=user,
            website=website,
        ).delete()

        return deleted_count