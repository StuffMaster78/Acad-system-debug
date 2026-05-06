import uuid
from django.db import models


class AuditEvent(models.Model):
    """
    Immutable system-wide audit event ledger.

    This is the source of truth for all system actions across:
    - Orders
    - Special Orders (including sensitive access tracking)
    - Communications
    - Auth / Permissions
    """

    # -------------------------
    # Identity
    # -------------------------
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        db_index=True,
    )
    # -------------------------
    # Time
    # -------------------------
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # -------------------------
    # Actor (who did it)
    # -------------------------
    actor_id = models.BigIntegerField(null=True, blank=True, db_index=True)

    actor_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Optional: user, system, admin, service"
    )

    # -------------------------
    # Action (what happened)
    # -------------------------
    action = models.CharField(max_length=255, db_index=True)

    # Examples:
    # order.created
    # order.status_changed
    # special_order.sensitive_viewed
    # message.edited
    # permission.granted

    # -------------------------
    # Object reference (what it happened to)
    # -------------------------
    object_type = models.CharField(
        max_length=255,
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

    processed_at = models.DateTimeField(null=True, blank=True)
    processing_attempts = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)

    # -------------------------
    # Request context (traceability)
    # -------------------------
    request_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
    )

    # -------------------------
    # Sensitivity / compliance layer
    # (critical for your special orders system)
    # -------------------------
    is_sensitive = models.BooleanField(
        default=False,
        db_index=True,
    )

    sensitivity_level = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="e.g. low, medium, high, restricted"
    )

    access_context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Who accessed what sensitive data and under what condition"
    )

    parent_span_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
    )
    span_depth = models.IntegerField(default=0)

    span_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True
    )
    span_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    span_start_ms = models.BigIntegerField(null=True, blank=True)
    span_duration_ms = models.BigIntegerField(null=True, blank=True)

    # -------------------------
    # Flexible metadata (bounded usage)
    # -------------------------
    metadata = models.JSONField(default=dict, blank=True)

    # Recommended structure:
    # {
    #   "from": "pending",
    #   "to": "paid",
    #   "field": "status"
    # }

    # -------------------------
    # System origin (important for debugging)
    # -------------------------
    source = models.CharField(
        max_length=100,
        default="system",
        db_index=True
    )
    # e.g.:
    # "orders_service"
    # "communications_app"
    # "middleware"
    # "admin_action"

    class Meta:
        indexes = [
            models.Index(fields=["actor_id", "timestamp"]),
            models.Index(fields=["object_type", "object_id"]),
            models.Index(fields=["action", "timestamp"]),
            models.Index(fields=["is_sensitive", "timestamp"]),
            models.Index(fields=["request_id"]),
        ]
        ordering = ["-timestamp"]


    def save(self, *args, **kwargs):
        if self.pk:
            raise RuntimeError(
                "AuditEvent is immutable and cannot be updated"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.action} | {self.actor_id} | {self.timestamp}"