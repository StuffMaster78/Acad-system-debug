from __future__ import annotations

import uuid
from django.db import models


class AuditSeverity(models.TextChoices):
    INFO = "info", "Info"
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class AuditStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSED = "processed", "Processed"
    FAILED = "failed", "Failed"
    DISCARDED = "discarded", "Discarded"


class AuditEvent(models.Model):

    # -------------------------
    # Identity
    # -------------------------

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="audit_events",
        db_index=True,
    )

    # -------------------------
    # Time
    # -------------------------

    occurred_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    # -------------------------
    # Actor
    # -------------------------

    actor_id = models.BigIntegerField(
        null=True,
        blank=True,
        db_index=True,
    )

    # -------------------------
    # Action
    # -------------------------

    action = models.CharField(
        max_length=255,
        db_index=True,
    )

    # -------------------------
    # Object
    # -------------------------

    object_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
    )

    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    # -------------------------
    # Lifecycle
    # -------------------------

    status = models.CharField(
        max_length=20,
        choices=AuditStatus.choices,
        default=AuditStatus.PENDING,
        db_index=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    processing_attempts = models.PositiveIntegerField(
        default=0,
    )

    last_error = models.TextField(
        null=True,
        blank=True,
    )
    integrity_hash = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )

    previous_hash = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )

    # -------------------------
    # Request context
    # -------------------------

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        null=True,
        blank=True,
    )

    # -------------------------
    # Trace (FIXED TYPES)
    # -------------------------

    correlation_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    span_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
    )

    # -------------------------
    # Severity
    # -------------------------

    severity = models.CharField(
        max_length=20,
        choices=AuditSeverity.choices,
        default=AuditSeverity.INFO,
        db_index=True,
    )

    is_sensitive = models.BooleanField(
        default=False,
        db_index=True,
    )

    sensitivity_level = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    # -------------------------
    # Origin
    # -------------------------

    service_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
    )

    # -------------------------
    # Metadata
    # -------------------------

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    # -------------------------
    # Reliability
    # -------------------------

    event_version = models.PositiveIntegerField(default=1)

    idempotency_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    # -------------------------
    # Meta
    # -------------------------

    class Meta:
        ordering = ["-occurred_at"]

        indexes = [
            models.Index(fields=["website", "occurred_at"]),
            models.Index(fields=["website", "action"]),
            models.Index(fields=["website", "actor_id"]),
            models.Index(fields=["object_type", "object_id"]),
            models.Index(fields=["correlation_id"]),
            models.Index(fields=["span_id"]),
            models.Index(fields=["status", "processed_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "idempotency_key"],
                name="uniq_audit_event_idempotency_per_website",
            )
        ]

    # -------------------------
    # IMMUTABILITY
    # -------------------------

    IMMUTABLE_FIELDS = {
        "website",
        "actor_id",
        "action",
        "object_type",
        "object_id",
        "ip_address",
        "user_agent",
        "metadata",
        "correlation_id",
        "span_id",
        "is_sensitive",
        "sensitivity_level",
        "service_name",
        "severity",
        "idempotency_key",
    }

    def save(self, *args, **kwargs):
        if self.pk:
            previous = AuditEvent.objects.get(pk=self.pk)

            for field in self.IMMUTABLE_FIELDS:
                old = getattr(previous, field)
                new = getattr(self, field)

                # FK-safe comparison
                if field == "website":
                    old = old_id if (old_id := getattr(old, "id", None)) else None
                    new = getattr(new, "id", None)

                if old != new:
                    raise RuntimeError(f"AuditEvent field '{field}' is immutable.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} | actor={self.actor_id} | {self.occurred_at}"