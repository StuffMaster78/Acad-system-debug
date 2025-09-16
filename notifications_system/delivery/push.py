from __future__ import annotations

import logging
from typing import Any, Dict

from notifications_system.delivery.base import (
    BaseDeliveryBackend,
    DeliveryResult,
)

logger = logging.getLogger(__name__)


class PushBackend(BaseDeliveryBackend):
    """Push delivery backend.

    Sends push notifications to mobile or web apps through a provider
    such as FCM or OneSignal. This implementation is provider-agnostic;
    inject your client call in the marked section.

    Returns:
        DeliveryResult indicating success, message, and optional meta.

    Notes:
        * Keep this idempotent if possible so retries are safe.
        * Avoid including secrets in logs or `meta`.
    """

    channel = "push"

    def send(self) -> DeliveryResult:
        """Send a push notification via the configured provider.

        Returns:
            DeliveryResult describing provider outcome.
        """
        user = self.user
        payload: Dict[str, Any] = dict(self.notification.payload or {})

        title = (
            payload.get("title")
            or getattr(self.notification, "title", None)
            or "Notification"
        )
        body = (
            payload.get("message")
            or getattr(self.notification, "message", None)
            or ""
        )

        # Device tokens / endpoints should be resolved from your user
        # or a related table. Example expects attr `device_tokens`.
        tokens = getattr(user, "device_tokens", None) or []
        if not tokens:
            return DeliveryResult(
                success=False,
                message="no device tokens for user",
                meta={"user_id": getattr(user, "id", None)},
            )

        # Build a minimal provider payload. Extend as needed
        # (click_action, image, badge, sound, data, etc.).
        data = {
            "title": title,
            "body": body,
            "event": self.notification.event,
            "link": (payload.get("link") or ""),
        }
        data_extra = payload.get("data") or {}
        data.update(data_extra)

        try:
            # --- Provider call (stub) ---------------------------------
            # Replace the following block with your FCM/OneSignal client.
            #
            # Example (pseudo):
            #   resp = fcm_client.send(tokens=tokens, notification=data)
            #   ok = resp.success_count == len(tokens)
            #   meta = {"success": resp.success_count, "failure": ...}
            #
            # For now we log and pretend success.
            logger.info(
                "Push send to user=%s tokens=%d event=%s",
                getattr(user, "id", None),
                len(tokens),
                self.notification.event,
            )
            ok = True
            meta = {"tokens": len(tokens)}
            # -----------------------------------------------------------

            if ok:
                return DeliveryResult(
                    success=True,
                    message="push sent",
                    meta=meta,
                )
            return DeliveryResult(
                success=False,
                message="push provider reported failure",
                meta=meta,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Push send failed: %s", exc)
            return DeliveryResult(
                success=False,
                message=f"send failed: {exc}",
                meta={"tokens": len(tokens)},
            )

    def supports_retry(self) -> bool:
        """Return True if push sends are idempotent in your provider."""
        return True