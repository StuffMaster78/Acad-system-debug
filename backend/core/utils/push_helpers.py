# core/utils/push_helpers.py
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

FCM_API_URL = "https://fcm.googleapis.com/fcm/send"

def send_push_notification(device_token, title, message):
    """
    Send a push notification to a specific device via Firebase Cloud Messaging (FCM).

    Args:
        device_token: The device token of the recipient's device.
        title: The title of the push notification.
        message: The body content of the push notification.

    Returns:
        True if the notification was sent successfully, False otherwise.
    """
    if not device_token:
        logger.error("No device token provided for push notification.")
        return False

    headers = {
        "Authorization": f"key={settings.FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": device_token,
        "notification": {
            "title": title,
            "body": message,
            "sound": "default"  # Optional: Play the default sound for the notification
        },
        "priority": "high",  # Optional: Priority of the notification
    }

    try:
        response = requests.post(FCM_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            logger.info(f"Push notification sent to {device_token}: {title}")
            return True
        else:
            logger.error(f"Failed to send push notification: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        return False


def send_push_notification_to_group(group_name, title, message):
    """
    Send a push notification to all users in a group.

    Args:
        group_name: The name of the group (e.g., "admins", "writers").
        title: The title of the push notification.
        message: The body content of the push notification.

    Returns:
        True if the notification was sent to all group members, False otherwise.
    """
    # Fetch all device tokens for the group (from your database or cache)
    # This assumes you have a mechanism for storing and retrieving device tokens for groups
    device_tokens = get_device_tokens_for_group(group_name)

    if not device_tokens:
        logger.warning(f"No device tokens found for group {group_name}")
        return False

    success = True
    for token in device_tokens:
        if not send_push_notification(token, title, message):
            success = False

    return success


def get_device_tokens_for_group(group_name):
    """
    Fetches device tokens for all users in the specified group.
    
    For example, you can store the tokens in your database and retrieve them here.
    This is a mock implementation, and you should replace it with real logic.
    
    Args:
        group_name: The name of the group (e.g., "admins", "writers").
    
    Returns:
        A list of device tokens.
    """
    # For the purpose of this example, returning mock data
    # In production, you'll fetch device tokens from your database.
    return [
        "device_token_1",
        "device_token_2",
        "device_token_3"
    ]