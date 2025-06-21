from typing import TYPE_CHECKING, Any, Optional
from enum import Enum
from orders.models import Order
from writer_management.models import WebhookPlatform
from django.contrib.auth import get_user_model
from django.utils import timezone

# User = get_user_model()


if TYPE_CHECKING:
    from users.models import User

def build_webhook_payload(
        event: str,
        order: Order,
        triggered_by: Optional["User"],
        platform: str = WebhookPlatform.SLACK,
        test: bool = False,
        fallback_icon: str = None,
) -> dict:
    """
    Generates a rich payload for a webhook event, tailored per platform.

    Args:
        event (str): Event name (e.g. order_assigned)
        order (Order): The order object
        triggered_by (User): The actor causing the event
        platform (str): slack or discord
        test (bool): If True, adds dummy/test markers

    Returns:
        dict: Payload formatted for the webhook
    """
    base = {
        "event": event,
        "order_id": order.id,
        "order_title": order.title,
        "status": order.status,
        "triggered_by": {
            "id": triggered_by.id if triggered_by else None,
            "name": (triggered_by.get_full_name() or triggered_by.username) if triggered_by else "System",
            "role": getattr(triggered_by, "role", "unknown") if triggered_by else "system",
        },
        "fallback_icon": fallback_icon or "https://yourcdn.com/default-avatar.png",
        "message_preview": f"📦 Order #{order.id} – {event.replace('_', ' ').title()}",
        "test_mode": test,
    }

    if platform == WebhookPlatform.SLACK:
        return build_slack_payload(base)

    elif platform == WebhookPlatform.DISCORD:
        return build_discord_payload(base)

    return base  # fallback

def format_slack_payload(payload):
    return {
        "text": f"📢 *{payload['event'].replace('_', ' ').title()}*",
        "attachments": [
            {
                "title": payload["order_title"],
                "fields": [
                    {"title": "Order ID", "value": payload["order_id"], "short": True},
                    {"title": "Status", "value": payload["status"], "short": True},
                    {"title": "Deadline", "value": payload["deadline"] or "N/A", "short": True},
                ],
                "footer": f"Triggered by: {payload['triggered_by']['name']}" if payload["triggered_by"] else "",
                "ts": timezone.now().timestamp(),
            }
        ]
    }

def build_slack_payload(data: dict) -> dict:
    return {
        "text": data["message_preview"],
        "attachments": [
            {
                "title": f"Order #{data['order_id']}",
                "fields": [
                    {"title": "Event", "value": data["event"], "short": True},
                    {"title": "Status", "value": data["status"], "short": True},
                    {"title": "Triggered By", "value": data["triggered_by"]["name"], "short": False},
                ],
                "color": "#36a64f" if not data.get("test_mode") else "#e0e0e0",
            }
        ]
    }


def build_discord_payload(data: dict) -> dict:
    return {
        "content": data["message_preview"],
        "embeds": [
            {
                "title": f"Order #{data['order_id']}",
                "fields": [
                    {"name": "Event", "value": data["event"], "inline": True},
                    {"name": "Status", "value": data["status"], "inline": True},
                    {"name": "Triggered By", "value": data["triggered_by"]["name"], "inline": False},
                ],
                "color": 3066993 if not data.get("test_mode") else 8355711,
            }
        ]
    }