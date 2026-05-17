from __future__ import annotations

import uuid
from django.db import models


class Command(models.Model):
    """
    Immutable intent from superadmin layer.
    Never directly mutates data.
    """

    class Status(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"
        EXECUTED = "executed"
        FAILED = "failed"
        CANCELLED = "cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant_id = models.BigIntegerField(db_index=True)
    actor_id = models.BigIntegerField(db_index=True)

    command_type = models.CharField(max_length=100, db_index=True)
    payload = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    requires_approval = models.BooleanField(default=False)

    correlation_id = models.UUIDField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)