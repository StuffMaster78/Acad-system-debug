from .base import BaseDeliveryBackend
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer # type: ignore
import logging

logger = logging.getLogger(__name__)


class WebSocketBackend(BaseDeliveryBackend):
    """
    Sends real-time notifications via Django Channels.
    Requires a running channel layer and a subscribed frontend.
    """

    def send(self):
        user = self.notification.user
        website = self.notification.website
        payload = self.notification.payload or {}
        config = self.channel_config or {}

        group_name = config.get("group_override") or f"notifications_{user.id}"
        channel_layer = get_channel_layer()

        if not channel_layer:
            logger.error("WebSocket delivery failed: No channel layer configured.")
            return False

        event_payload = {
            "type": "send_notification",
            "notification": {
                "id": self.notification.id,
                "title": payload.get("title") or self.notification.title,
                "message": payload.get("message") or self.notification.message,
                "timestamp": self.notification.created_at.isoformat(),
                "extra": payload.get("extra", {}),
            }
        }

        try:
            async_to_sync(channel_layer.group_send)(group_name, event_payload)
            return True
        except Exception as e:
            logger.error(
                f"Failed to send WebSocket notification [{self.notification.id}] to group [{group_name}]: {e}",
                exc_info=True
            )
            return False

    def supports_retry(self):
        # You *could* implement retry with Redis Streams or Celery fallback if wanted.
        return False