from __future__ import annotations

import uuid
from django.db import models


class Policy(models.Model):
    """
    Versioned policy definition (Git-style governance).
    """

    class Effect(models.TextChoices):
        ALLOW = "allow"
        DENY = "deny"
        REQUIRE_APPROVAL = "require_approval"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    tenant_id = models.BigIntegerField(db_index=True, null=True, blank=True)

    version = models.IntegerField(default=1)

    is_active = models.BooleanField(default=True)

    effect = models.CharField(max_length=30, choices=Effect.choices)

    # JSON rule definition (DSL / AST / conditions)
    rule = models.JSONField()

    priority = models.IntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)


class PolicyVersion(models.Model):
    """
    Git-like history for audit + rollback.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    policy_id = models.UUIDField(db_index=True)

    version = models.IntegerField()

    snapshot = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)


class PolicyDecisionLog(models.Model):
    """
    Every evaluation is recorded (Stripe Radar style).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    command_id = models.UUIDField(db_index=True)

    actor_id = models.BigIntegerField()

    tenant_id = models.BigIntegerField()

    decision = models.CharField(max_length=50) # allow/deny/approval

    matched_policies = models.JSONField(default=list)

    risk_score = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)