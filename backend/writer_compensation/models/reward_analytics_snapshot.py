from __future__ import annotations

from decimal import Decimal

from django.db import models

from websites.models.websites import Website


class RewardAnalyticsSnapshot(
    models.Model,
):
    """
    Daily reward analytics snapshot.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name=(
            "reward_analytics_snapshots"
        ),
    )

    snapshot_date = models.DateField()

    rewards_issued = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    total_bonus_amount = (
        models.DecimalField(
            max_digits=12,
            decimal_places=2,
            default=Decimal("0.00"),
        )
    )

    fraud_flags = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    elite_writers = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-snapshot_date",
        ]

        unique_together = (
            "website",
            "snapshot_date",
        )

    def __str__(self) -> str:
        return (
            f"{self.website.pk} | "
            f"{self.snapshot_date}"
        )