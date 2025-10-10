# notifications_system/tasks.py
from __future__ import annotations
import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from notifications_system.models.delivery import Delivery
from notifications_system.models.outbox import Outbox
from notifications_system.services.dispatcher import queue_delivery
from notifications_system.services.outbox import mark_processed
from notifications_system.services.providers.base import (
    choose_provider, TemporaryProviderError
)

log = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def process_outbox(self, outbox_id: int) -> None:
    ob = Outbox.objects.filter(id=outbox_id, processed_at__isnull=True).first()
    if not ob:
        return
    try:
        channels = ob.payload.get("channels") or ["in_app", "email"]
        priority = ob.payload.get("priority") or "medium"
        dedupe = ob.dedupe_key or f"{ob.event_key}:{ob.user_id}"
        queue_delivery(
            event_key=ob.event_key,
            website_id=ob.website_id,
            user_id=ob.user_id,
            payload=ob.payload,
            channels=channels,
            priority=priority,
            dedupe_key=dedupe,
        )
        mark_processed(ob, ok=True)
    except Exception as exc:
        mark_processed(ob, ok=False, err=str(exc))
        raise self.retry(exc=exc)

@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_delivery(self, delivery_id: int) -> None:
    d = Delivery.objects.filter(id=delivery_id, status="queued").first()
    if not d:
        return
    try:
        provider = choose_provider(d.channel)
        resp = provider.send(d.rendered, d)
        with transaction.atomic():
            d.status = "sent"
            d.provider = resp.provider
            d.provider_msg_id = resp.message_id
            d.sent_at = timezone.now()
            d.attempts += 1
            d.save(update_fields=[
                "status", "provider", "provider_msg_id",
                "sent_at", "attempts",
            ])
    except TemporaryProviderError as exc:
        d.attempts += 1
        d.error_code = getattr(exc, "code", "temporary")
        d.error_detail = str(exc)[:1000]
        d.save(update_fields=["attempts", "error_code", "error_detail"])
        raise self.retry(exc=exc)
    except Exception as exc:
        d.attempts += 1
        d.status = "failed"
        d.error_code = "permanent"
        d.error_detail = str(exc)[:1000]
        d.save(update_fields=["attempts", "status", "error_code", "error_detail"])
        log.exception("Delivery %s failed", d.id)