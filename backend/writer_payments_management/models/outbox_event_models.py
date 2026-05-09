from __future__ import annotations

import hashlib
import json

from django.db import models


class OutboxEvent(models.Model):
    """
    Durable event log for async processing.

    GUARANTEE:
        Each event is processed at least once,
        but must behave like exactly-once via idempotency.
    """

    event_type = models.CharField(max_length=100)

    payload = models.JSONField(default=dict)

    # CRITICAL: prevents duplicates at DB level
    payload_hash = models.CharField(max_length=64, db_index=True)

    processed = models.BooleanField(default=False)
    processing = models.BooleanField(default=False)

    retry_count = models.PositiveIntegerField(default=0)

    last_error = models.TextField(null=True, blank=True)

    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event_type", "payload_hash"],
                name="uniq_outbox_event_type_payload",
            )
        ]

    def save(self, *args, **kwargs):
        if not self.payload_hash:
            self.payload_hash = self._generate_hash()
        super().save(*args, **kwargs)

    def _generate_hash(self) -> str:
        raw = json.dumps(self.payload, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()