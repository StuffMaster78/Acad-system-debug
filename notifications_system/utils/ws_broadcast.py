import asyncio
import logging
import json
from channels.layers import get_channel_layer # type: ignore
from asgiref.sync import async_to_sync, iscoroutinefunction

logger = logging.getLogger(__name__)

def push_ws_notification(user_id, message: dict):
    """
    Push a WebSocket notification to a specific user.
    """
    group_name = f"notifications_{user_id}"
    channel_layer = get_channel_layer()

    try:
        async_func = channel_layer.group_send
        payload = {
            "type": "send.notification",
            "message": message
        }

        if iscoroutinefunction(async_func):
            # In an async context (e.g. ASGI, Celery 5+ with asyncio)
            return asyncio.create_task(channel_layer.group_send(group_name, payload))
        else:
            # In sync context (views, most code paths)
            return async_to_sync(channel_layer.group_send)(group_name, payload)
    except Exception as e:
        logger.error(f"WebSocket push failed for {group_name}: {e}", exc_info=True)