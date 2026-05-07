import uuid

from django.db import models


class AuditDeadLetter(models.Model):
    """
    Persistent failed audit-event recovery store.
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

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
    )

    event_payload = models.JSONField()

    error_message = models.TextField()

    retry_count = models.PositiveIntegerField(default=0)

    max_retries = models.PositiveIntegerField(default=5)

    is_resolved = models.BooleanField(
        default=False,
        db_index=True,
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
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
    )

    span_duration_ms = models.BigIntegerField(
        null=True,
        blank=True,
    )

    last_retry_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    failed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ["-failed_at"]

        indexes = [
            models.Index(
                fields=["is_resolved", "failed_at"]
            ),
            models.Index(
                fields=["retry_count", "max_retries"]
            ),
            models.Index(
                fields=["website", "is_resolved"]
            ),
        ]