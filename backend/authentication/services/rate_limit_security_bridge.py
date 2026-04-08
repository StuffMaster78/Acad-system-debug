"""
Rate limit to security event bridge.

Promote important rate-limit events into the central SecurityEvent
timeline when the abuse pattern is meaningful.
"""

from datetime import timedelta

from django.utils import timezone

from authentication.models.rate_limit_event import RateLimitEvent
from authentication.models.security_events import SecurityEvent
from authentication.services.security_event_service import (
    SecurityEventService,
)


class RateLimitSecurityBridgeService:
    """
    Bridge noisy throttle telemetry into meaningful security events.
    """

    DEFAULT_LOOKBACK_MINUTES = 15

    @classmethod
    def record_rate_limit_event(
        cls,
        *,
        user,
        website,
        ip_address: str,
        user_agent: str = "",
        path: str,
        method: str,
        reason: str,
    ) -> RateLimitEvent:
        """
        Record a rate-limit event and promote it to SecurityEvent when
        appropriate.

        Args:
            user: User instance or None.
            website: Website instance or None.
            ip_address: Client IP address.
            user_agent: Optional user agent string.
            path: Request path.
            method: HTTP method.
            reason: Rate-limit reason.

        Returns:
            Created RateLimitEvent instance.
        """
        rate_limit_event = RateLimitEvent.objects.create(
            user=user,
            website=website,
            ip_address=ip_address,
            user_agent=user_agent,
            path=path,
            method=method,
            reason=reason,
        )

        cls._maybe_log_security_event(
            rate_limit_event=rate_limit_event,
        )

        return rate_limit_event

    @classmethod
    def _maybe_log_security_event(
        cls,
        *,
        rate_limit_event: RateLimitEvent,
    ) -> None:
        """
        Promote a rate-limit event to SecurityEvent when thresholds are
        met or the reason is inherently sensitive.

        Args:
            rate_limit_event: Newly created RateLimitEvent instance.
        """
        website = rate_limit_event.website
        user = rate_limit_event.user
        ip_address = rate_limit_event.ip_address
        reason = rate_limit_event.reason

        if website is None:
            return

        severity = SecurityEvent.Severity.LOW
        should_promote = False

        # Sensitive reasons can be promoted immediately
        if reason in {
            RateLimitEvent.Reason.MFA_THROTTLE,
            RateLimitEvent.Reason.PASSWORD_RESET_THROTTLE,
            RateLimitEvent.Reason.DEVICE_RISK_THROTTLE,
        }:
            should_promote = True
            severity = SecurityEvent.Severity.MEDIUM

        # Repeated recent abuse should also be promoted
        recent_count = cls._get_recent_rate_limit_count(
            website=website,
            ip_address=ip_address,
            user=user,
            reason=reason,
        )

        if recent_count >= 3:
            should_promote = True
            severity = SecurityEvent.Severity.MEDIUM

        if recent_count >= 6:
            severity = SecurityEvent.Severity.HIGH

        if not should_promote:
            return

        SecurityEventService.log(
            user=user,
            website=website,
            event_type=SecurityEvent.EventType.SUSPICIOUS_ACTIVITY,
            severity=severity,
            is_suspicious=True,
            ip_address=ip_address,
            user_agent=rate_limit_event.user_agent,
            metadata={
                "source": "rate_limit_event",
                "reason": reason,
                "path": rate_limit_event.path,
                "method": rate_limit_event.method,
                "recent_count": recent_count,
                "rate_limit_event_id": rate_limit_event.pk,
            },
        )

    @classmethod
    def _get_recent_rate_limit_count(
        cls,
        *,
        website,
        ip_address: str,
        user,
        reason: str,
        lookback_minutes: int = DEFAULT_LOOKBACK_MINUTES,
    ) -> int:
        """
        Count recent matching rate-limit events.

        Args:
            website: Website instance.
            ip_address: Client IP address.
            user: User instance or None.
            reason: Rate-limit reason.
            lookback_minutes: Lookback window.

        Returns:
            Count of recent matching events.
        """
        threshold = timezone.now() - timedelta(
            minutes=lookback_minutes,
        )

        queryset = RateLimitEvent.objects.filter(
            website=website,
            reason=reason,
            triggered_at__gte=threshold,
        )

        if user is not None:
            queryset = queryset.filter(user=user)
        else:
            queryset = queryset.filter(ip_address=ip_address)

        return queryset.count()