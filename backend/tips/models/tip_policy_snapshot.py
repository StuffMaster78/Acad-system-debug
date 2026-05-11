from __future__ import annotations

from django.db import models


class TipPolicySnapshot(models.Model):
    """
    Immutable snapshot of the policy applied to a tip.

    Preserves the exact policy configuration used when calculating
    the financial settlement.
    """

    tip = models.OneToOneField(
        "tips.Tip",
        on_delete=models.CASCADE,
        related_name="policy_snapshot",
    )

    policy_name = models.CharField(
        max_length=255,
    )

    policy_version = models.PositiveIntegerField()

    writer_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    platform_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return (
            f"{self.policy_name} "
            f"(v{self.policy_version})"
        )