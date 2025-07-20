from .base import BaseDeliveryBackend
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging

logger = logging.getLogger(__name__)

class WebSocketBackend(BaseDeliveryBackend):
    """
    Sends real-time notifications via Django Channels.
    """

    def send(self):
        user = self.notification.user
        group = f"notifications_{user.id}"

        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.error("No channel layer configured.")
            return False

        try:
            async_to_sync(channel_layer.group_send)(
                group,
                {
                    "type": "send_notification",
                    "message": self.notification.as_dict()
                }
            )
            return True
        except Exception as e:
            logger.error(f"WebSocket send failed: {e}", exc_info=True)
            return False