from __future__ import annotations

import uuid
from django.db import models


class ApprovalWorkflow(models.Model):
    """
    A single approval instance created from a command.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    command_type = models.CharField(max_length=255)
    command_payload = models.JSONField()

    actor_id = models.IntegerField()
    tenant_id = models.IntegerField()

    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "pending"),
            ("approved", "approved"),
            ("rejected", "rejected"),
            ("executed", "executed"),
            ("expired", "expired"),
        ],
        default="pending",
    )

    current_node = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ApprovalNodeState(models.Model):
    """
    Tracks per-node progress in a DAG.
    """

    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name="node_states",
    )

    node_id = models.CharField(max_length=255)

    approved_by = models.JSONField(default=list)
    rejected_by = models.JSONField(default=list)

    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "pending"),
            ("completed", "completed"),
            ("rejected", "rejected"),
        ],
        default="pending",
    )


class ApprovalAction(models.Model):
    """
    Immutable audit trail of every approval decision.
    """

    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name="actions",
    )

    node_id = models.CharField(max_length=255)

    actor_id = models.IntegerField()

    action = models.CharField(
        max_length=20,
        choices=[("approve", "approve"), ("reject", "reject")],
    )

    timestamp = models.DateTimeField(auto_now_add=True)