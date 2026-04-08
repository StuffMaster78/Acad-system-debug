import logging
from typing import Any

import requests


logger = logging.getLogger(__name__)


class SecurityAlertService:
    """
    Handle outbound security alerts for authentication-related events.

    This service is responsible for dispatching security notifications
    such as IP blocks, suspicious login activity, and related alerts to
    external webhooks or downstream monitoring systems.

    Enforcement logic should not live here. This service should be
    called by orchestration or security services after an event occurs.
    """

    DEFAULT_TIMEOUT_SECONDS = 5

    @staticmethod
    def get_webhook_url(*, website) -> str | None:
        """
        Resolve the security webhook URL for a website.

        Args:
            website: Website or tenant instance.

        Returns:
            Configured webhook URL, or None if unavailable.
        """
        return getattr(website, "security_webhook_url", None)

    @classmethod
    def send_ip_block_alert(
        cls,
        *,
        website,
        ip_address: str,
        reason: str,
        duration_minutes: int,
    ) -> bool:
        """
        Send a security alert for a blocked IP address.

        Args:
            website: Website or tenant instance.
            ip_address: Blocked IP address.
            reason: Reason the IP was blocked.
            duration_minutes: Duration of the block in minutes.

        Returns:
            True if the alert was sent successfully, otherwise False.
        """
        payload = {
            "event_type": "ip_blocked",
            "website_id": getattr(website, "pk", None),
            "ip_address": ip_address,
            "reason": reason,
            "duration_minutes": duration_minutes,
        }

        return cls._post_webhook(
            website=website,
            payload=payload,
        )

    @classmethod
    def send_suspicious_login_alert(
        cls,
        *,
        website,
        user=None,
        ip_address: str | None = None,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Send a security alert for suspicious login activity.

        Args:
            website: Website or tenant instance.
            user: Optional user instance associated with the event.
            ip_address: Optional source IP address.
            reason: Human-readable reason for the alert.
            metadata: Optional additional context.

        Returns:
            True if the alert was sent successfully, otherwise False.
        """
        payload = {
            "event_type": "suspicious_login",
            "website_id": getattr(website, "pk", None),
            "user_id": getattr(user, "pk", None) if user else None,
            "ip_address": ip_address,
            "reason": reason,
            "metadata": metadata or {},
        }

        return cls._post_webhook(
            website=website,
            payload=payload,
        )

    @classmethod
    def _post_webhook(
        cls,
        *,
        website,
        payload: dict[str, Any],
    ) -> bool:
        """
        Post a security payload to the configured webhook endpoint.

        Args:
            website: Website or tenant instance.
            payload: Security event payload.

        Returns:
            True if the webhook call succeeded, otherwise False.
        """
        webhook_url = cls.get_webhook_url(website=website)

        if not webhook_url:
            logger.info(
                "No security webhook configured for website_id=%s",
                getattr(website, "pk", None),
            )
            return False

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=cls.DEFAULT_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            logger.exception(
                "Failed to send security webhook for website_id=%s",
                getattr(website, "pk", None),
            )
            return False