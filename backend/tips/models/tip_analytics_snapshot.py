from __future__ import annotations

from decimal import Decimal

from django.db import models


class TipAnalyticsSnapshot(models.Model):
    """
    Pre-aggregated analytics snapshot for tipping system.

    This model exists to avoid expensive runtime aggregation
    across large tip datasets.

    It is primarily used for:
    - dashboards
    - finance reporting
    - revenue analytics
    - writer earnings summaries
    """

    date = models.DateField(
        db_index=True,
    )

    writer = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="tip_snapshots",
    )

    total_gross_tips = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_writer_earnings = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_platform_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    tip_count = models.PositiveIntegerField(
        default=0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-date"]
        unique_together = ["date", "writer"]
        indexes = [
            models.Index(
                fields=["date"],
                name="tip_analytics_date_idx",
            ),
            models.Index(
                fields=["writer", "date"],
                name="tip_analytics_writer_date_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Analytics {self.writer.pk} "
            f"on {self.date}"
        )