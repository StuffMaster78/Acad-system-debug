# core/utils/ws_helpers.py
import json
from channels.layers import get_channel_layer
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_channel_layer():
    """
    Returns the channel layer to interact with WebSocket groups.
    Uses Django's channel layers.
    """
    try:
        return get_channel_layer()
    except Exception as e:
        logger.error(f"Error initializing channel layer: {e}")
        raise

def send_ws_notification(user, message, group_name=None):
    """
    Sends a WebSocket notification to a user or a group of users.
    
    Args:
        user: The user to notify. The user must have a valid WebSocket connection.
        message: The message to send over WebSocket.
        group_name: Optional; group to broadcast the message to. If not provided, 
                     sends to the individual user's WebSocket channel.

    Returns:
        True if the message was sent, False otherwise.
    """
    if not user.is_authenticated:
        logger.warning(f"User {user.username} is not authenticated.")
        return False  # Don't send notifications to unauthenticated users.

    # Use group_name for broadcasting, otherwise send to the user individually
    channel_layer = get_channel_layer()

    try:
        if group_name:
            # Send to the group (i.e., multiple users in a group)
            channel_layer.group_send(
                group_name,
                {
                    'type': 'send_notification',  # This will be handled by your consumer's method
                    'message': message
                }
            )
        else:
            # Send directly to the user (individual WebSocket)
            channel_layer.send(
                f'notifications_{user.id}',
                {
                    'type': 'send_notification',  # Will be handled by the consumer
                    'message': message
                }
            )

        logger.info(f"WebSocket message sent to {user.username}: {message}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WebSocket notification to {user.username}: {e}")
        return False