from django.db import transaction
from django.db.models import F
from audit_logging.models.audit_dead_letter import AuditDeadLetter


class DeadLetterQueueStore:
    """
    Single source of truth for failed audit events.
    """

    DEFAULT_BATCH_SIZE = 50

    @classmethod
    def push(cls, *, event_data: dict, error: str) -> AuditDeadLetter:
        return AuditDeadLetter.objects.create(
            event_payload=event_data,
            error_message=error,
        )

    @classmethod
    def fetch_batch(cls, limit: int | None = None):
        batch_size = limit or cls.DEFAULT_BATCH_SIZE

        return (
            AuditDeadLetter.objects
            .filter(
                is_resolved=False,
                retry_count__lt=F("max_retries"),
            )
            .order_by("failed_at")  # FIXED (was created_at)
        )[:batch_size]

    @classmethod
    @transaction.atomic
    def mark_resolved(cls, item: AuditDeadLetter) -> None:
        (
            AuditDeadLetter.objects
            .select_for_update()
            .filter(pk=item.pk)
            .update(is_resolved=True)
        )

    @classmethod
    @transaction.atomic
    def increment_retry(cls, item: AuditDeadLetter) -> None:
        (
            AuditDeadLetter.objects
            .select_for_update()
            .filter(pk=item.pk)
            .update(retry_count=F("retry_count") + 1)
        )