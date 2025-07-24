from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer # type: ignore
from notifications_system.tasks.notifications import async_send_ws_notification
import logging

logger = logging.getLogger(__name__)

def send_ws_notification(user, message, payload=None, **kwargs):
    """
    Send a WebSocket notification to the given user.
    """
    if not user or not user.is_authenticated:
        logger.warning(f"Cannot send WS notification: Invalid user {user}")
        return

    group_name = f"notifications_{user.id}"
    use_async = kwargs.get('use_async', False)

    if use_async:
        async_send_ws_notification.delay(user.id, payload)
        return
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