import uuid

from django.db import models


class AuditSpan(models.Model):
    """
    Execution trace span.

    Represents an operational execution unit.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        db_index=True,
    )

    correlation_id = models.CharField(
        max_length=255,
        db_index=True,
    )

    span_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
    )

    parent_span_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
    )

    name = models.CharField(
        max_length=255,
    )

    depth = models.PositiveIntegerField(default=0)

    source = models.CharField(
        max_length=100,
        default="system",
        db_index=True,
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    duration_ms = models.BigIntegerField(
        null=True,
        blank=True,
    )

    is_error = models.BooleanField(
        default=False,
        db_index=True,
    )

    error_message = models.TextField(
        null=True,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )
    status = models.CharField(
        choices=[
            ("running", "Running"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ]
    )

    class Meta:
        ordering = ["-started_at"]

        indexes = [
            models.Index(
                fields=["website", "started_at"]
            ),
            models.Index(
                fields=["correlation_id", "started_at"]
            ),
            models.Index(
                fields=["parent_span_id"]
            ),
        ]


    IMMUTABLE_FIELDS = {
        "website_id",
        "correlation_id",
        "span_id",
        "parent_span_id",
        "name",
        "depth",
        "source",
    }

    def save(self, *args, **kwargs):
        if self.pk:
            old = AuditSpan.objects.get(pk=self.pk)

            for field in self.IMMUTABLE_FIELDS:
                if getattr(old, field) != getattr(self, field):
                    raise RuntimeError(
                        f"AuditSpan field '{field}' is immutable"
                    )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.span_id})"