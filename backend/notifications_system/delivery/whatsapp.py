from __future__ import annotations

import logging
from typing import Any, Dict

from notifications_system.delivery.base import (
    BaseDeliveryBackend,
    DeliveryResult,
)

logger = logging.getLogger(__name__)


class WhatsAppBackend(BaseDeliveryBackend):
    """WhatsApp delivery backend.

    Sends notifications via a WhatsApp messaging provider. This backend
    assumes an external integration (e.g., Twilio WhatsApp API).

    Channel config keys:
      * Any provider-specific options required by your integration.

    Returns:
      DeliveryResult with success flag and optional provider meta.
    """

    channel = "whatsapp"

    def send(self) -> DeliveryResult:
        """Send a WhatsApp message to the user's phone number.

        Returns:
            DeliveryResult describing provider outcome.
        """
        user = self.user
        payload: Dict[str, Any] = dict(self.notification.payload or {})
        cfg: Dict[str, Any] = dict(self.channel_config or {})

        phone = getattr(
            getattr(user, "profile", None),
            "phone_number",
            None,
        )
        if not phone:
            msg = "No phone number found for WhatsApp delivery"
            logger.warning("[WhatsApp] %s (user=%s)", msg, getattr(user, "id", None))
            return DeliveryResult(
                success=False,
                message=msg,
                meta={"user_id": getattr(user, "id", None)},
            )

        try:
            message = (
                payload.get("message")
                or getattr(self.notification, "message", None)
                or ""
            )
            # Stubbed provider call:
            #   send_whatsapp_message(phone, message, config=cfg)
            logger.info(
                "[WhatsApp] Sending message to %s: %s", phone, message
            )
            return DeliveryResult(
                success=True,
                message="whatsapp sent",
                meta={"phone": phone},
            )
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "[WhatsApp] Exception sending to %s: %s", phone, exc, exc_info=True
            )
            return DeliveryResult(
                success=False,
                message=f"send failed: {exc}",
                meta={"phone": phone},
            )

    def supports_retry(self) -> bool:
        """Return True; WhatsApp messages are safe to retry."""
        return True