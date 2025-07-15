# writer_management.models.performance.py

from django.db import models
from django.utils.timezone import now
from websites.models import Website
from writer_management.models.profile import WriterProfile


class WriterPerformanceSnapshot(models.Model):
    """
    Weekly or monthly snapshot of a writer’s performance.

    Used for ranking, promotion, strike logic, leveling, and insights.
    """

    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        related_name="writer_performance_snapshots"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="performance_snapshots"
    )

    # Time window
    period_start = models.DateField()
    period_end = models.DateField()

    # Output metrics
    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)
    late_orders = models.PositiveIntegerField(default=0)
    revised_orders = models.PositiveIntegerField(default=0)
    disputed_orders = models.PositiveIntegerField(default=0)
    hvo_orders = models.PositiveIntegerField(default=0)  # High value

    # Pages and preferred orders
    total_pages = models.PositiveIntegerField(default=0)
    preferred_orders = models.PositiveIntegerField(default=0)

    # Earnings
    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    bonuses = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    tips = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    client_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        help_text="Total client revenue for writer’s orders"
    )
    profit_contribution = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        help_text="Client revenue - writer cost"
    )

    # Ratings
    average_rating = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True)

    # Composite / calculated
    completion_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0.0)
    lateness_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0.0)
    revision_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0.0)
    dispute_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0.0)
    preferred_order_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0.0)

    average_turnaround_hours = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)

    composite_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Weighted score used to compare writer performance"
    )
    better_than_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Percent of writers this one outperforms in the same period"
    )

    # Caching/metadata
    is_cached = models.BooleanField(default=False)
    generated_at = models.DateTimeField(default=now)

    class Meta:
        verbose_name = "Writer Performance Snapshot"
        verbose_name_plural = "Writer Performance Snapshots"
        unique_together = ("website", "writer", "period_start", "period_end")
        indexes = [
            models.Index(fields=["website", "writer", "period_end"]),
        ]

    def __str__(self):
        return (
            f"{self.writer.user.username} performance "
            f"{self.period_start} → {self.period_end}"
        )