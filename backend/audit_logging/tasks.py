import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.db import transaction
from django.utils import timezone

from audit_logging.models.audit_event import AuditEvent
from audit_logging.selectors.audit_selectors import AuditSelectors
from audit_logging.models.audit_dead_letter import AuditDeadLetter

logger = logging.getLogger("audit")


@shared_task(bind=True, max_retries=3)
def process_audit_event_task(self, audit_id: str):
    event = None

    try:
        with transaction.atomic():
            event = AuditSelectors.claim_unprocessed_event(audit_id)

            if not event:
                return

            event.processing_attempts += 1
            event.save(update_fields=["processing_attempts"])

        # outside lock (correct for long-running work)
        _process_event(event)

        event.processed_at = timezone.now()
        event.last_error = None
        event.status = "processed"
        event.save(update_fields=["processed_at", "last_error", "status"])

    except Exception as exc:

        if event:
            event.last_error = str(exc)
            event.status = "failed"
            event.save(update_fields=["last_error", "status"])

        logger.exception(
            "Audit event processing failed",
            extra={"audit_id": audit_id},
        )

        try:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)

        except MaxRetriesExceededError:
            send_to_dlq(audit_id)


# --------------------------------------------------
# DLQ HANDLER
# --------------------------------------------------

def send_to_dlq(audit_id: str):
    try:
        event = AuditEvent.objects.get(id=audit_id)

        AuditDeadLetter.objects.create(
            event_id=event.id,
            website=event.website,

            event_payload={
                "audit_event_id": str(event.id),
                "action": event.action,
                "actor_id": event.actor_id,
                "metadata": event.metadata,
                "object_type": event.object_type,
                "object_id": event.object_id,
                "correlation_id": event.correlation_id,
                "span_id": event.span_id,
                "is_sensitive": event.is_sensitive,
            },

            error_message=event.last_error or "unknown error",
            retry_count=event.processing_attempts,
        )

    except Exception:
        logger.exception(
            "Failed to write to DLQ",
            extra={"audit_id": audit_id},
        )


# --------------------------------------------------
# PROCESSOR HOOK
# --------------------------------------------------

def _process_event(event: AuditEvent):
    """
    Deterministic side-effect layer.

    MUST be:
    - idempotent
    - stateless
    - safe to retry
    """

    if event.action.startswith("billing."):
        pass

    if event.is_sensitive:
        pass