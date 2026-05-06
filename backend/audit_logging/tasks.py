import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from audit_logging.storage.models import AuditEvent
from audit_logging.selectors.audit_selectors import AuditSelectors
from audit_logging.storage.models_dlq import AuditDeadLetter

logger = logging.getLogger("audit")


@shared_task(bind=True, max_retries=3)
def process_audit_event_task(self, event_id: str):
    event = None

    try:
        # -------------------------
        # Lock + idempotency check
        # -------------------------
        with transaction.atomic():
            event = AuditSelectors.get_unprocessed(event_id)

            if not event:
                return

            # mark attempt safely
            event.processing_attempts += 1
            event.save(update_fields=["processing_attempts"])

        # -------------------------
        # DO ACTUAL WORK (outside lock)
        # -------------------------
        _process_event(event)

        # -------------------------
        # mark success
        # -------------------------
        event.processed_at = timezone.now()
        event.last_error = None
        event.save(update_fields=["processed_at", "last_error"])

    except Exception as exc:

        if event:
            event.last_error = str(exc)
            event.save(update_fields=["last_error"])

        logger.exception(
            "Audit event processing failed",
            extra={"event_id": event_id},
        )

        try:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)
        except self.MaxRetriesExceededError:
            send_to_dlq(event_id)


def send_to_dlq(event_id: str):
    try:
        event = AuditEvent.objects.get(event_id=event_id)

        AuditDeadLetter.objects.create(
            event_id=event.event_id,
            event_payload={
                "action": event.action,
                "metadata": event.metadata,
            },
            error=event.last_error,

            # trace context (if present)
            span_id=event.span_id,
            span_name=event.span_name,
            span_start_ms=event.span_start_ms,
            span_duration_ms=event.span_duration_ms,
        )

    except Exception:
        logger.exception(
            "Failed to write to DLQ",
            extra={"event_id": event_id},
        )


# -------------------------
# LOCAL processing hook
# -------------------------
def _process_event(event: AuditEvent):
    """
    Safe, idempotent processing layer.

    Keep this LIGHT and deterministic.
    Expand later as needed.
    """

    # Example hooks (you can extend later)
    if event.action.startswith("billing."):
        pass

    if event.is_sensitive:
        pass