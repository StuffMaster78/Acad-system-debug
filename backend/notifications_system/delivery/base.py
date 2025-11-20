from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class DeliveryResult:
    """Result of a backend delivery attempt.

    Attributes:
        success: Whether the delivery succeeded.
        message: Short, human-readable explanation for logs.
        meta: Optional provider response (IDs, codes). Safe for logs.
    """
    success: bool
    message: str = ""
    meta: Optional[Dict[str, Any]] = None


class BaseDeliveryBackend(ABC):
    """Abstract base for all delivery backends.

    Backends must:
      * Set ``channel`` to a stable string key (e.g., "email", "in_app").
      * Implement :meth:`send` and return :class:`DeliveryResult`.
      * Avoid sleeping/backoff; the service orchestrates retries.

    Args:
        notification: The persisted notification instance.
        channel_config: Optional per-channel configuration.
    """

    channel: str = "unknown"

    def __init__(
        self,
        notification,
        channel_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.notification = notification
        self.channel_config = channel_config or {}

    @property
    def user(self):
        """Return the user associated with the notification."""
        return self.notification.user

    @property
    def website(self):
        """Return the website/tenant for the notification."""
        return self.notification.website

    def prepare_context(self) -> Dict[str, Any]:
        """Build a canonical template context for renderers.

        Returns:
            Dict with payload, rendered fields, and useful objects.
        """
        payload = dict(self.notification.payload or {})
        rendered = {
            "title": (
                getattr(self.notification, "rendered_title", None)
                or payload.get("title")
            ),
            "text": (
                getattr(self.notification, "rendered_message", None)
                or payload.get("message")
            ),
            "html": (
                (self.channel_config or {}).get("html_message")
                or payload.get("html")
            ),
        }
        return {
            "payload": payload,
            "_rendered": rendered,
            "_user": self.user,
            "_website": self.website,
            "_notification": self.notification,
            "_config": self.channel_config,
        }

    def supports_retry(self) -> bool:
        """Return whether this backend is safe to retry.

        The service decides when to retry. Override when idempotent.

        Returns:
            True if safe to retry; otherwise False.
        """
        return False

    @abstractmethod
    def send(self) -> DeliveryResult:
        """Execute the delivery attempt.

        Returns:
            DeliveryResult describing the outcome.

        Raises:
            Only raise for programmer/config errors. Routine failures
            should be expressed via the returned DeliveryResult.
        """
        raise NotImplementedError