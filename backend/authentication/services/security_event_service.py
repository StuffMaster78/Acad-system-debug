"""
Security event service.

Provide a consistent way to record security-relevant events across the
authentication and account-security system.
"""

from typing import Any

from authentication.models.security_events import SecurityEvent


class SecurityEventService:
    """
    Centralized helper for logging security events consistently.
    """

    @staticmethod
    def log(
        *,
        user,
        website,
        event_type: str,
        severity: str = SecurityEvent.Severity.LOW,
        is_suspicious: bool = False,
        ip_address: str | None = None,
        location: str | None = None,
        device: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityEvent:
        """
        Log a security event.

        Args:
            user: User instance.
            website: Website instance.
            event_type: Event type value.
            severity: Severity value.
            is_suspicious: Whether event is suspicious.
            ip_address: Optional IP address.
            location: Optional human-readable location.
            device: Optional device summary.
            user_agent: Optional user agent string.
            metadata: Optional structured metadata.

        Returns:
            Created SecurityEvent instance.
        """
        return SecurityEvent.log_event(
            user=user,
            website=website,
            event_type=event_type,
            severity=severity,
            is_suspicious=is_suspicious,
            ip_address=ip_address,
            location=location,
            device=device,
            user_agent=user_agent,
            metadata=metadata or {},
        )

    @staticmethod
    def log_from_request(
        *,
        request,
        user,
        website,
        event_type: str,
        severity: str = SecurityEvent.Severity.LOW,
        is_suspicious: bool = False,
        metadata: dict[str, Any] | None = None,
        location: str | None = None,
        device: str | None = None,
    ) -> SecurityEvent:
        """
        Log a security event using context derived from an HTTP request.

        Args:
            request: HTTP request object.
            user: User instance.
            website: Website instance.
            event_type: Event type value.
            severity: Severity value.
            is_suspicious: Whether event is suspicious.
            metadata: Optional structured metadata.
            location: Optional location string.
            device: Optional device summary override.

        Returns:
            Created SecurityEvent instance.
        """
        ip_address = None
        user_agent = ""

        if request is not None:
            ip_address = request.META.get("REMOTE_ADDR")
            user_agent = request.META.get("HTTP_USER_AGENT", "")

        return SecurityEventService.log(
            user=user,
            website=website,
            event_type=event_type,
            severity=severity,
            is_suspicious=is_suspicious,
            ip_address=ip_address,
            location=location,
            device=device,
            user_agent=user_agent,
            metadata=metadata,
        )