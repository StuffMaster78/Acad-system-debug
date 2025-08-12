from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer  # type: ignore
from notifications_system.tasks.notifications import (
    async_send_ws_notification
)
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
    use_async = kwargs.get("use_async", False)
    payload = payload or {}

    if use_async:
        async_send_ws_notification.delay(user.id, payload)
        return

    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            raise RuntimeError(
                "CHANNEL_LAYERS is not configured in Django settings"
            )
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "data": {
                    "title": "New Notification",
                    "message": message,
                    "payload": payload,
                },
            },
        )
        logger.info(f"WS notification queued for user_id={user.id}")
    except Exception as e:
        logger.error(
            f"WS notify failed for user_id={user.id}: {e}", exc_info=True
        )