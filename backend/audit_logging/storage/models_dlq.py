import uuid
from django.db import models


class AuditDeadLetter(models.Model):
    """
    Persistent storage for failed audit events.

    This is your recovery backbone.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    event_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    event_payload = models.JSONField()

    error = models.TextField()

    retry_count = models.IntegerField(default=0)

    max_retries = models.IntegerField(default=5)

    is_resolved = models.BooleanField(
        default=False,
        db_index=True,
    )
    span_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )
    span_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    span_start_ms = models.BigIntegerField(
        null=True,
        blank=True,
    )
    span_duration_ms = models.BigIntegerField(
        null=True,
        blank=True,
    )

    last_retry_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    failed_at = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["is_resolved", "created_at"]),
            models.Index(fields=["retry_count"]),
        ]