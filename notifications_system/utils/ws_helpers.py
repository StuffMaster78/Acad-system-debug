from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging

logger = logging.getLogger(__name__)

def send_ws_notification(user, message, payload=None):
    """
    Send a WebSocket notification to the given user.
    """
    if not user or not user.is_authenticated:
        logger.warning(f"Cannot send WS notification: Invalid user {user}")
        return

    group_name = f"notifications_{user.id}"

    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "data": {
                    "title": "New Notification",
                    "message": message,
                    "payload": payload or {},
                }
        }
        )
        logger.info(f"WebSocket notification queued for {user}")
    except Exception as e:
        logger.error(f"Failed to send WS notification to {user}: {e}", exc_info=True)