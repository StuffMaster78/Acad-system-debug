from __future__ import annotations

from django.db import models
from django.utils import timezone


class IdempotencyRecord(models.Model):
    """
    Prevents duplicate side effects across distributed compensation flows.
    """

    key = models.CharField(max_length=255)
    scope = models.CharField(max_length=100)

    request_hash = models.CharField(max_length=255, blank=True, null=True)

    response = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["key", "scope"],
                name="unique_idempotency_key_scope",
            )
        ]
        indexes = [
            models.Index(fields=["key", "scope"]),
        ]

    def __str__(self) -> str:
        return f"{self.scope}:{self.key}"
