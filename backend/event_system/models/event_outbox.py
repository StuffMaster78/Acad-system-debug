import uuid
from django.db import models


class EventStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing"
    PROCESSED = "processed", "Processed"
    FAILED = "failed", "Failed"
    IGNORED = "ignored", "Ignored"
    DEAD_LETTER = "dead_letter", "Dead Letter"


class EventOutbox(models.Model):
    """
    Reliable event delivery outbox (production-grade).

    This is a transport layer, NOT a domain model.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Strongly typed event identity
    event_type = models.CharField(
        max_length=120,
        db_index=True,
    )

    # Domain grouping (reviews, reputation, compensation, etc.)
    domain = models.CharField(
        max_length=60,
        db_index=True,
    )

    # Versioning for safe evolution
    version = models.PositiveIntegerField(default=1)

    # Fully structured event payload (validated elsewhere)
    payload = models.JSONField(default=dict)

    # Routing metadata (precomputed for dispatchers)
    routing_key = models.CharField(
        max_length=200,
        db_index=True,
    )

    # Idempotency protection
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
    )

    status = models.CharField(
        max_length=30,  # EventStatus
        choices=EventStatus.choices,
        default=EventStatus.PENDING,
        db_index=True,
    )

    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)

    # Traceability (critical for production debugging)
    correlation_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    causation_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )
    last_error = models.TextField(
        null=True,
        blank=True,
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ignored_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["domain", "event_type"]),
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["routing_key"]),
        ]

    def __str__(self) -> str:
        return f"{self.domain}:{self.event_type} ({self.status})"