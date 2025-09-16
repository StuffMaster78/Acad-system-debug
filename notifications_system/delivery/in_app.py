from __future__ import annotations

import logging

from notifications_system.delivery.base import (
    BaseDeliveryBackend,
    DeliveryResult,
)

logger = logging.getLogger(__name__)


class InAppBackend(BaseDeliveryBackend):
    """In-app delivery backend.

    This backend confirms that the notification is available for the
    in-app UI. The service already persists the notification model
    instance; we do not mutate status here to avoid racing with the
    service's final status updates and logs.

    Returns:
        DeliveryResult indicating success.
    """

    channel = "in_app"

    def send(self) -> DeliveryResult:
        """Return success for in-app availability.

        You can extend this to push an immediate realtime signal
        (e.g., SSE or WebSocket) if desired.

        Returns:
            DeliveryResult with success=True on standard path.
        """
        try:
            # No-op by default. The Notification is already persisted by
            # the service and will be fetched by the frontend via API.
            return DeliveryResult(success=True, message="in_app available")
        except Exception as exc:  # noqa: BLE001
            logger.exception("InAppBackend error: %s", exc)
            return DeliveryResult(False, f"in_app failed: {exc}")

    def supports_retry(self) -> bool:
        """Return False; in-app has nothing to retry."""
        return False