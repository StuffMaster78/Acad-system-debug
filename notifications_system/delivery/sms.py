from __future__ import annotations

import logging
from typing import Any, Dict

from notifications_system.delivery.base import (
    BaseDeliveryBackend,
    DeliveryResult,
)
from notifications_system.utils.sms_helpers import send_sms_notification

logger = logging.getLogger(__name__)


class SMSBackend(BaseDeliveryBackend):
    """SMS delivery backend.

    Sends SMS notifications via a pluggable utility function. The utility
    may wrap Twilio, Africa's Talking, or another provider.

    Channel config keys:
      * Any provider-specific options accepted by send_sms_notification.

    Returns:
      DeliveryResult indicating provider outcome.
    """

    channel = "sms"

    def send(self) -> DeliveryResult:
        """Send an SMS to the user's phone number.

        Returns:
            DeliveryResult with success flag and optional provider meta.
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
            logger.warning("[SMS] No phone number for user %s", getattr(user, "id", None))
            return DeliveryResult(
                success=False,
                message="no phone number",
                meta={"user_id": getattr(user, "id", None)},
            )

        try:
            message = (
                payload.get("message")
                or getattr(self.notification, "message", None)
                or ""
            )
            success = send_sms_notification(phone, message, config=cfg)

            if success:
                return DeliveryResult(
                    success=True,
                    message="sms sent",
                    meta={"phone": phone},
                )
            logger.warning("[SMS] Delivery failed to %s", phone)
            return DeliveryResult(
                success=False,
                message="sms provider failure",
                meta={"phone": phone},
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("[SMS] Exception while sending to %s: %s", phone, exc)
            return DeliveryResult(
                success=False,
                message=f"send failed: {exc}",
                meta={"phone": phone},
            )

    def supports_retry(self) -> bool:
        """Return True; SMS sends are usually safe to retry."""
        return True