from __future__ import annotations

from django.db import models

from websites.models.websites import Website


class SettlementRuleSnapshot(models.Model):
    """
    Freezes financial rules at time of settlement.

    Prevents retroactive fairness disputes.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="settlement_rule_snapshots",
    )

    settlement_period = models.ForeignKey(
        "writer_payments_management.SettlementPeriod",
        on_delete=models.CASCADE,
        related_name="rule_snapshot",
    )

    rules = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)