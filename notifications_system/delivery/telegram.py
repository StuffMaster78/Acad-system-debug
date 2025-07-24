from .base import BaseDeliveryBackend
import logging
import requests # type: ignore

logger = logging.getLogger(__name__)


class TelegramBackend(BaseDeliveryBackend):
    """
    Sends notification to Telegram via Bot API.
    Expects `telegram_chat_id` in the channel_config or on the user profile.
    """

    TELEGRAM_API_URL = "https://api.telegram.org"

    def send(self):
        user = self.notification.user
        website = self.notification.website
        payload = self.notification.payload or {}
        config = self.channel_config or {}

        bot_token = config.get("bot_token")
        chat_id = config.get("chat_id") or getattr(user, "telegram_chat_id", None)
        message = payload.get("message") or self.notification.message

        if not bot_token or not chat_id:
            logger.warning(
                f"Missing Telegram config for notification {self.notification.id}. "
                f"bot_token or chat_id not set."
            )
            return False

        url = f"{self.TELEGRAM_API_URL}/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",  # or "HTML"
        }

        try:
            response = requests.post(url, json=data, timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(
                f"Failed to send Telegram notification {self.notification.id}: {e}",
                exc_info=True
            )
            return False

    def supports_retry(self):
        return True