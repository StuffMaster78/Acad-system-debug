"""
Historical analytics snapshots.

This model exists for:
- dashboards
- charts
- trend analysis
- ranking history
- reporting

Snapshots are immutable.
Usually generated daily by scheduled jobs.
"""

from django.db import models
from decimal import Decimal

class WriterMetricsSnapshot(models.Model):
    """
    Immutable writer analytics snapshot.
    """

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="metric_snapshots",
    )

    snapshot_date = models.DateField(
        db_index=True,
    )

    completed_orders = models.PositiveIntegerField(
        default=0,
    )

    active_orders = models.PositiveIntegerField(
        default=0,
    )

    cancelled_orders = models.PositiveIntegerField(
        default=0,
    )

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    lateness_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    revision_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_penalties = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Writer Metrics Snapshot"
        verbose_name_plural = "Writer Metrics Snapshots"
        ordering = ["-snapshot_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["writer", "snapshot_date"],
                name="unique_writer_snapshot_per_day",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterMetricsSnapshot<"
            f"{self.writer.id}:{self.snapshot_date}"
            f">"
        )