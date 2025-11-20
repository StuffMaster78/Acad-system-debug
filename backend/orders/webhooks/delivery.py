from orders.order_enums import WebhookEvent
from writer_management.models import WebhookSettings
from orders.webhooks.payloads import build_webhook_payload
import requests

class WebhookDeliveryService:

    @staticmethod
    def send_order_event(user, event: str, payload: dict):
        """
        Sends a webhook event to the user's configured webhook URL.
        Args:
            user: The user to whom the webhook is sent.
            event (str): The event type, e.g., 'order_created', 'order_updated'.
            payload (dict): The data to send in the webhook.
        """
        try:
            settings = user.webhook_settings
        except WebhookSettings.DoesNotExist:
            return  # No settings? No ping.

        if not settings.enabled or event not in settings.subscribed_events:
            return  # Not enabled or opted out

        # Build payload
        data = build_webhook_payload(event=event, payload=payload, user=user)

        # Send request (optionally queue via Celery)
        try:
            requests.post(settings.webhook_url, json=data, timeout=5)
        except Exception as e:
            # Log it, retry with Celery later if needed
            print(f"Webhook send failed for {user}: {e}")
