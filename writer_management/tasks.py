from celery import shared_task
import requests # type: ignore
import logging
from .utils import WebhookPayloadFormatter
from django.core.exceptions import ValidationError
from writer_management.models import WebhookSettings
from writer_management.models import WebhookPlatform
from orders.order_enums import  WebhookEvent

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def deliver_webhook_payload(
    self, webhook_url, payload,
    platform, user_id, event_type
):
    """
    Task to deliver a webhook payload.
    Retries on failure.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Platform": platform,
        "X-User-ID": str(user_id),
        "X-Event-Type": event_type,
    }

    try:
        formatted = WebhookPayloadFormatter.format(event_type, payload, platform)
        resp = requests.post(
            webhook_url, json=formatted,
            headers=headers, timeout=5
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning(f"Webhook delivery {platform} failed: {exc}")
        raise self.retry(
            exc=exc, countdown=10 * (self.request.retries + 1)
        )