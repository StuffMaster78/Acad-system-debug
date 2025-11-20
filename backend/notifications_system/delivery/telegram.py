from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import requests  # type: ignore

from notifications_system.delivery.base import (
    BaseDeliveryBackend,
    DeliveryResult,
)

logger = logging.getLogger(__name__)


class TelegramBackend(BaseDeliveryBackend):
    """Telegram delivery backend.

    Sends notifications via the Telegram Bot API. Requires a bot token
    and a chat ID. These may be provided in ``channel_config`` or as
    attributes on the user model.

    Channel config keys:
      * bot_token: Telegram bot token string (required).
      * chat_id: Telegram chat ID (optional if user.telegram_chat_id set).

    Returns:
      DeliveryResult with provider response outcome.
    """

    channel = "telegram"
    TELEGRAM_API_URL = "https://api.telegram.org"

    def send(self) -> DeliveryResult:
        """Send the notification via Telegram Bot API.

        Returns:
            DeliveryResult indicating success/failure and meta info.
        """
        user = self.user
        payload: Dict[str, Any] = dict(self.notification.payload or {})
        cfg: Dict[str, Any] = dict(self.channel_config or {})

        bot_token: Optional[str] = cfg.get("bot_token")
        chat_id: Optional[str] = (
            cfg.get("chat_id") or getattr(user, "telegram_chat_id", None)
        )
        message = (
            payload.get("message")
            or getattr(self.notification, "message", None)
            or ""
        )

        if not bot_token or not chat_id:
            msg = "Missing Telegram bot_token or chat_id"
            logger.warning("%s (notification=%s)", msg, self.notification.id)
            return DeliveryResult(
                success=False,
                message=msg,
                meta={"user_id": getattr(user, "id", None)},
            )

        url = f"{self.TELEGRAM_API_URL}/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

        try:
            resp = requests.post(url, json=data, timeout=5)
            resp.raise_for_status()
            return DeliveryResult(
                success=True,
                message="telegram sent",
                meta={"chat_id": chat_id, "status": resp.status_code},
            )
        except requests.RequestException as exc:
            logger.error(
                "Telegram send failed for notification=%s: %s",
                self.notification.id,
                exc,
                exc_info=True,
            )
            return DeliveryResult(
                success=False,
                message=f"send failed: {exc}",
                meta={"chat_id": chat_id},
            )

    def supports_retry(self) -> bool:
        """Return True; Telegram sends are safe to retry."""
        return True