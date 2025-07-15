from django.db import models
from decimal import Decimal
from django.utils.timezone import now
from websites.models import Website
from writer_management.models.profile import WriterProfile


class WriterPerformanceMetrics(models.Model):
    """
    Aggregated weekly performance snapshot for a writer.
    Used to support leveling, dashboards, and incentives.
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        related_name="writer_metrics"
    )
    writer = models.ForeignKey(
        WriterProfile, on_delete=models.CASCADE,
        related_name="performance_metrics"
    )

    week_start = models.DateField()
    week_end = models.DateField()

    avg_turnaround_time = models.DurationField(null=True, blank=True)
    avg_rating = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    revision_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    dispute_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    lateness_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    cancellation_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    acceptance_to_completion_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    preferred_order_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00
    )
    total_orders_completed = models.PositiveIntegerField(default=0)
    total_pages_completed = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    total_tips = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    total_bonuses = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    total_fines = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    total_profit_contribution = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Client pay - Writer earnings"
    )
    hvo_orders_completed = models.PositiveIntegerField(default=0)

    composite_score = models.DecimalField(
        max_digits=6, decimal_places=2,
        default=Decimal("0.00")
    )
    percentile_rank = models.DecimalField(
        max_digits=6, decimal_places=2,
        default=Decimal("0.00"),
        help_text="You’re better than X% of writers"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website", "writer", "week_start")
        ordering = ["-week_start"]
        verbose_name = "Writer Performance Metrics"
        verbose_name_plural = "Writer Performance Metrics"

    def __str__(self):
        return (
            f"{self.writer.user.username} - "
            f"{self.week_start} → {self.week_end}"
        )

    def as_dict(self):
        return {
            "avg_turnaround_time": self.avg_turnaround_time,
            "avg_rating": self.avg_rating,
            "revision_rate": self.revision_rate,
            "dispute_rate": self.dispute_rate,
            "lateness_rate": self.lateness_rate,
            "cancellation_rate": self.cancellation_rate,
            "acceptance_to_completion_ratio":
                self.acceptance_to_completion_ratio,
            "preferred_order_rate": self.preferred_order_rate,
            "total_orders_completed": self.total_orders_completed,
            "total_pages_completed": self.total_pages_completed,
            "total_earnings": self.total_earnings,
            "total_tips": self.total_tips,
            "total_bonuses": self.total_bonuses,
            "total_fines": self.total_fines,
            "total_profit_contribution": self.total_profit_contribution,
            "hvo_orders_completed": self.hvo_orders_completed,
            "composite_score": self.composite_score,
            "percentile_rank": self.percentile_rank,
        }
