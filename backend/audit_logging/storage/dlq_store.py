from audit_logging.storage.models_dlq import AuditDeadLetter
from django.db import models

class DeadLetterQueueStore:

    @classmethod
    def push(cls, event_data: dict, error: str):
        AuditDeadLetter.objects.create(
            event_payload=event_data,
            error_message=error,
        )

    @classmethod
    def fetch_batch(cls, limit=50):
        return AuditDeadLetter.objects.filter(
            is_resolved=False,
            retry_count__lt=models.F("max_retries"),
        ).order_by("created_at")[:limit]

    @classmethod
    def mark_resolved(cls, item):
        item.is_resolved = True
        item.save(update_fields=["is_resolved"])

    @classmethod
    def increment_retry(cls, item):
        item.retry_count += 1
        item.save(update_fields=["retry_count"])