from celery import shared_task
import requests
import logging
from orders.webhooks.payloads import build_webhook_payload
from orders.models import Order
from users.models import User  # adjust path if different
from writer_management.models import WebhookSettings
from audit_logging.services import WebhookAuditLogger
from orders.webhooks.payloads import build_webhook_payload
from orders.models import WebhookDeliveryLog

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_webhook_task(self, webhook_url, payload):
    try:
        requests.post(webhook_url, json=payload, timeout=5)
    except Exception as exc:
        self.retry(exc=exc, countdown=5)

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_webhook_task(self, webhook_url: str, payload: dict, headers: dict = None):
    """
    Sends a webhook request to the given URL with the provided payload.

    Args:
        webhook_url (str): The URL to which the webhook is sent.
        payload (dict): The payload to send.
        headers (dict, optional): Additional headers, e.g., Content-Type, auth.

    Retries:
        Retries up to 3 times on failure, with a 10-second delay between attempts.
    """
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers or {"Content-Type": "application/json"},
            timeout=5
        )
        response.raise_for_status()

        logger.info(f"✅ Webhook sent to {webhook_url} | Status: {response.status_code}")

    except requests.exceptions.RequestException as exc:
        logger.warning(f"❌ Webhook failed for {webhook_url}: {exc}")
        self.retry(exc=exc)




@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_webhook_notification(self, order_id: int, user_id: int, event: str, test: bool = False):
    """
    Celery task to send webhook notification to writer.

    Args:
        order_id: ID of the order.
        user_id: ID of the user to notify.
        event: The event type (e.g. "order_assigned").
        test: Whether it's a test/preview payload.
    """
    try:
        order = Order.objects.get(id=order_id)
        user = User.objects.get(id=user_id)
        settings = user.webhook_settings

        if not settings.enabled or not settings.is_active:
            return

        if event not in settings.subscribed_events:
            return

        payload = build_webhook_payload(
            event=event,
            order=order,
            triggered_by=user if not test else user,  # optionally system/admin
            platform=settings.platform,
            test=test
        )

        headers = {
            "Content-Type": "application/json",
        }

        # Optional: Add user-defined headers or token auth if needed
        if hasattr(settings, "custom_headers") and settings.custom_headers:
            headers.update(settings.custom_headers)

        resp = requests.post(settings.webhook_url, json=payload, headers=headers, timeout=8)
        resp.raise_for_status()

        # Audit logging (optional)
        # WebhookLog.objects.create(...)

    except (Order.DoesNotExist, User.DoesNotExist, WebhookSettings.DoesNotExist):
        pass

    except requests.exceptions.RequestException as e:
        self.retry(exc=e)

    except Exception as e:
        # Log error in Sentry or logs
        raise e
    
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def deliver_webhook_task(
    self,
    *,
    user_id,
    platform,
    webhook_url,
    event,
    order_id,
    triggered_by_id,
    test=False,
    retry_count=0,
    fallback_icon=None
):
    from django.contrib.auth import get_user_model
    from orders.models import Order

    try:
        user = User.objects.get(pk=user_id)
        order = Order.objects.get(pk=order_id)
        triggered_by = User.objects.get(pk=triggered_by_id)

        payload = build_webhook_payload(
            event=event,
            order=order,
            triggered_by=triggered_by,
            platform=platform,
            test=test
        )

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)

        WebhookDeliveryLog.objects.create(
            user=user,
            website=order.website,
            event=event,
            url=webhook_url,
            success=response.status_code in [200, 204],
            status_code=response.status_code,
            response_body=response.text,
            request_payload=payload,
            test_mode=test,
            retry_count=retry_count,
        )

        if response.status_code not in [200, 204]:
            raise Exception(f"Webhook failed: {response.status_code}")

    except Exception as e:
        WebhookDeliveryLog.objects.create(
            user_id=user_id,
            website_id=Order.objects.get(pk=order_id).website_id,
            event=event,
            url=webhook_url,
            success=False,
            error_message=str(e),
            request_payload=payload,
            test_mode=test,
            retry_count=retry_count + 1
        )
        if retry_count < 2:
            raise self.retry(exc=e, countdown=2 ** retry_count)
       