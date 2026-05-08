import uuid

from django.db import models


class AuditDeadLetter(models.Model):
    """
    Persistent recovery storage for failed audit events.

    This acts as the final safety net when retries fail.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # ------------------------------------------------------------------
    # Tenant
    # ------------------------------------------------------------------

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="audit_dead_letters",
        db_index=True,
    )

    # ------------------------------------------------------------------
    # Event linkage
    # ------------------------------------------------------------------

    event_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Original AuditEvent ID if available",
    )

    # ------------------------------------------------------------------
    # Failure payload
    # ------------------------------------------------------------------

    event_payload = models.JSONField()

    error_message = models.TextField()

    # ------------------------------------------------------------------
    # Retry lifecycle
    # ------------------------------------------------------------------

    retry_count = models.PositiveIntegerField(
        default=0,
    )

    max_retries = models.PositiveIntegerField(
        default=5,
    )

    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    last_retry_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # Resolution lifecycle
    # ------------------------------------------------------------------

    is_resolved = models.BooleanField(
        default=False,
        db_index=True,
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # # ------------------------------------------------------------------
    # # Trace correlation
    # # ------------------------------------------------------------------

    # span_id = models.CharField(
    #     max_length=64,
    #     null=True,
    #     blank=True,
    #     db_index=True,
    # )

    # span_name = models.CharField(
    #     max_length=255,
    #     null=True,
    #     blank=True,
    # )

    # span_duration_ms = models.BigIntegerField(
    #     null=True,
    #     blank=True,
    # )

    # ------------------------------------------------------------------
    # Time
    # ------------------------------------------------------------------

    failed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    # ------------------------------------------------------------------
    # Model metadata
    # ------------------------------------------------------------------

    class Meta:
        ordering = ["-failed_at"]

        indexes = [
            models.Index(fields=["is_resolved", "failed_at"]),
            models.Index(fields=["website", "is_resolved"]),
            models.Index(fields=["retry_count", "max_retries"]),
            models.Index(fields=["event_id"]),
        ]

    def __str__(self):
        return (
            f"DLQ<{self.event_id}> | "
            f"resolved={self.is_resolved}"
        )