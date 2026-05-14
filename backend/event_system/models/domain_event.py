import uuid
from django.db import models


class DomainEvent(models.Model):
    """
    Persistent domain event log.

    This is the source of truth for all emitted events.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    event_type = models.CharField(
        max_length=100,
        db_index=True,
    )

    aggregate_id = models.UUIDField(
        db_index=True,
    )

    payload = models.JSONField(
        default=dict,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    is_processed = models.BooleanField(
        default=False,
        db_index=True,
    )

    retry_count = models.PositiveIntegerField(
        default=0,
    )

    last_error = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["event_type", "is_processed"]
            ),
        ]