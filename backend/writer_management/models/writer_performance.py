"""
writer_management/models/performance.py

Three performance models with three distinct purposes.

─────────────────────────────────────────────────────────────
WriterPerformance
─────────────────────────────────────────────────────────────
Lifetime running totals for a writer.
One row per writer. Updated incrementally after every order event
by performance_tracker_service using F() expressions.

Never queried for level progression decisions — use snapshots
for that. Used for:
    - Writer dashboard lifetime stats
    - Admin writer profile overview
    - Financial mirrors for fast reads (source: writer_compensation)

─────────────────────────────────────────────────────────────
WriterPerformanceSnapshot
─────────────────────────────────────────────────────────────
Frozen record of a writer's metrics for a specific time window.
Append-only. Never updated after creation.

Created by writer_metrics_snapshot_service on a Celery schedule
(weekly or monthly depending on config).

Used exclusively by:
    level_progression_service — promotion/demotion decisions
    composite_score_service — scoring input
    admin performance reports — trend visualisation

The composite_score and better_than_percent fields are computed
by composite_score_service AFTER snapshot creation and written
back to is_processed=True. Until then is_processed=False.

─────────────────────────────────────────────────────────────
WriterPerformanceMetrics
─────────────────────────────────────────────────────────────
Aggregated weekly metrics with ranking context.
One row per writer per week.

Created by performance_aggregator_service on weekly Celery task.
Used by dashboards, reward criteria evaluation.

Differs from WriterPerformanceSnapshot:
    Snapshot = frozen record for level progression (by period)
    Metrics = weekly aggregation with percentile rank (always weekly)

─────────────────────────────────────────────────────────────
WHAT WAS FIXED
─────────────────────────────────────────────────────────────
performance.py:
    - average_rating: ForeignKey(WriterReview) → DecimalField
    - total_earnings: PositiveIntegerField → DecimalField
    - Removed broken import of WriterReview
    - __str__ no longer accesses writer.user.username
    - WriterPerformanceReport.period_start/end: DateTimeField → DateField
    - Added missing fields: cancellation_rate, revision_count

performance_snapshot.py:
    - is_cached removed — meaningless field
    - __str__ fixed
    - unique_together → UniqueConstraint
    - Added is_processed flag for composite score pipeline

metrics.py:
    - as_dict() removed — belongs in serializer
    - __str__ fixed
    - unique_together → UniqueConstraint
    - percentile_rank max_digits corrected
"""

from decimal import Decimal

from django.db import models
from django.utils.timezone import now


# ════════════════════════════════════════════════════════════════════
# WriterPerformance — lifetime counters
# ════════════════════════════════════════════════════════════════════

class WriterPerformance(models.Model):
    """
    Lifetime performance counters for a writer.

    One row per writer. Created by signal on WriterProfile creation.

    MUTATION CONTRACT
    -----------------
    All counter fields are updated exclusively by
    performance_tracker_service using F() expressions inside
    atomic transactions. Never set directly.

    Example correct update:
        WriterPerformance.objects.filter(writer=profile).update(
            completed_orders=F("completed_orders") + 1,
            total_orders=F("total_orders") + 1,
            on_time_deliveries=F("on_time_deliveries") + 1,
        )

    FINANCIAL MIRRORS
    -----------------
    total_earnings, total_tips, total_bonuses, total_fines are
    cached from writer_compensation for fast dashboard reads.
    writer_compensation is the source of truth for these values.
    Reconciled by writer_metrics_snapshot_service weekly.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_performance",
    )
    writer = models.OneToOneField(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="performance",
    )

    # ----------------------------------------------------------------
    # ORDER COUNTERS
    # ----------------------------------------------------------------

    total_orders = models.PositiveIntegerField(
        default=0,
        help_text="All orders ever assigned to this writer.",
    )
    completed_orders = models.PositiveIntegerField(
        default=0,
        help_text="Orders completed successfully.",
    )
    pending_orders = models.PositiveIntegerField(
        default=0,
        help_text="Orders currently in progress.",
    )
    cancelled_orders = models.PositiveIntegerField(
        default=0,
        help_text="Orders cancelled after assignment.",
    )
    disputed_orders = models.PositiveIntegerField(
        default=0,
        help_text="Orders that were disputed by the client.",
    )
    late_deliveries = models.PositiveIntegerField(
        default=0,
        help_text="Orders submitted past the writer's internal deadline.",
    )
    on_time_deliveries = models.PositiveIntegerField(
        default=0,
        help_text="Orders submitted on or before internal deadline.",
    )
    revision_count = models.PositiveIntegerField(
        default=0,
        help_text="Total revision requests received across all orders.",
    )

    # ----------------------------------------------------------------
    # RATINGS
    # average_rating is a rolling lifetime average.
    # Recomputed by performance_tracker_service after each new rating
    # using the Welford online algorithm to avoid full recalculation.
    # Formula: new_avg = old_avg + (new_rating - old_avg) / new_count
    # ----------------------------------------------------------------

    average_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Rolling lifetime average rating (0.00–5.00). "
            "Recomputed by performance_tracker_service after each rating. "
            "Never set directly."
        ),
    )
    total_ratings = models.PositiveIntegerField(
        default=0,
        help_text="Total number of ratings received. Denominator for average.",
    )

    # ----------------------------------------------------------------
    # FINANCIAL MIRRORS (cached from writer_compensation)
    # ----------------------------------------------------------------

    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Lifetime gross earnings (mirrored from writer_compensation).",
    )
    total_tips_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Lifetime tips received (mirrored from tips app).",
    )
    total_bonuses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_fines = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Performance"
        verbose_name_plural = "Writer Performance"
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(average_rating__gte=Decimal("0.00")) &
                    models.Q(average_rating__lte=Decimal("5.00"))
                ),
                name="perf_avg_rating_range",
            ),
            models.CheckConstraint(
                condition=models.Q(total_earnings__gte=Decimal("0.00")),
                name="perf_total_earnings_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    completed_orders__lte=models.F("total_orders")
                ),
                name="perf_completed_le_total",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    on_time_deliveries__lte=models.F("completed_orders")
                ),
                name="perf_on_time_le_completed",
            ),
        ]

    def __str__(self) -> str:
        return f"WriterPerformance<{self.writer.id}>"


# ════════════════════════════════════════════════════════════════════
# WriterPerformanceSnapshot — frozen period record
# ════════════════════════════════════════════════════════════════════

class WriterPerformanceSnapshot(models.Model):
    """
    Frozen performance record for a specific time window.

    Append-only. Never updated after creation except:
        composite_score — written by composite_score_service
        better_than_percent — written by composite_score_service
        is_processed — set True after composite score is computed

    CREATION
    --------
    writer_metrics_snapshot_service creates one snapshot per writer
    per evaluation period (weekly or monthly).

    PROCESSING PIPELINE
    -------------------
    Step 1: writer_metrics_snapshot_service creates snapshot
            with raw counters. is_processed=False.
    Step 2: composite_score_service reads all snapshots for the
            period, computes scores and percentile ranks, writes
            composite_score, better_than_percent, is_processed=True.
    Step 3: level_progression_service reads processed snapshots
            and evaluates promotion/demotion.

    Only fully processed snapshots (is_processed=True) are used
    for level progression decisions.

    RATE FIELDS
    -----------
    Stored as proportions (0.0000–1.0000), not percentages.
    Display by multiplying by 100.
    Example: completion_rate=0.9500 means 95% completion rate.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_performance_snapshots",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="performance_snapshots",
    )

    # ----------------------------------------------------------------
    # TIME WINDOW
    # DateField not DateTimeField — periods are calendar dates.
    # ----------------------------------------------------------------

    period_start = models.DateField(db_index=True)
    period_end = models.DateField(db_index=True)

    # ----------------------------------------------------------------
    # ORDER VOLUME
    # ----------------------------------------------------------------

    total_orders = models.PositiveIntegerField(default=0)
    completed_orders = models.PositiveIntegerField(default=0)
    cancelled_orders = models.PositiveIntegerField(default=0)
    late_orders = models.PositiveIntegerField(default=0)
    revised_orders = models.PositiveIntegerField(default=0)
    disputed_orders = models.PositiveIntegerField(default=0)
    hvo_orders = models.PositiveIntegerField(
        default=0,
        help_text="High-value orders completed in this period.",
    )
    total_pages = models.PositiveIntegerField(default=0)
    preferred_orders = models.PositiveIntegerField(
        default=0,
        help_text="Orders matching writer's preferred subjects or types.",
    )

    # ----------------------------------------------------------------
    # FINANCIALS FOR THIS PERIOD
    # ----------------------------------------------------------------

    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total writer earnings for this period.",
    )
    bonuses = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
    )
    tips = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
    )
    client_revenue = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total client payment for orders in this period.",
    )
    profit_contribution = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
        help_text="client_revenue minus amount_paid.",
    )

    # ----------------------------------------------------------------
    # RATINGS
    # Null when no ratings were received in this period.
    # ----------------------------------------------------------------

    average_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average rating for this period. Null if no ratings received.",
    )

    # ----------------------------------------------------------------
    # RATE METRICS
    # Stored as proportions (0.0000–1.0000).
    # Multiply by 100 for percentage display.
    # ----------------------------------------------------------------

    completion_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        default=Decimal("0.0000"),
        help_text="completed_orders / total_orders. 0.9500 = 95%.",
    )
    lateness_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        default=Decimal("0.0000"),
        help_text="late_orders / completed_orders.",
    )
    revision_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        default=Decimal("0.0000"),
        help_text="revised_orders / completed_orders.",
    )
    dispute_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        default=Decimal("0.0000"),
        help_text="disputed_orders / completed_orders.",
    )
    cancellation_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        default=Decimal("0.0000"),
        help_text="cancelled_orders / total_orders.",
    )
    preferred_order_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        default=Decimal("0.0000"),
        help_text="preferred_orders / completed_orders.",
    )
    average_turnaround_hours = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        help_text="Mean hours from assignment to submission.",
    )

    # ----------------------------------------------------------------
    # COMPOSITE METRICS
    # Written by composite_score_service after snapshot creation.
    # Null until is_processed=True.
    # ----------------------------------------------------------------

    composite_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Weighted performance score for this period. "
            "Computed by composite_score_service. "
            "Used by level_progression_service. "
            "Null until is_processed=True."
        ),
    )
    better_than_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Percentile rank: writer outperforms X% of writers "
            "on this site in this period. "
            "Null until is_processed=True."
        ),
    )

    # ----------------------------------------------------------------
    # PROCESSING STATE
    # ----------------------------------------------------------------

    is_processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "False immediately after creation. "
            "Set True by composite_score_service once "
            "composite_score and better_than_percent are computed. "
            "level_progression_service only evaluates processed snapshots."
        ),
    )
    generated_at = models.DateTimeField(
        default=now,
        help_text="When this snapshot was generated.",
    )

    class Meta:
        verbose_name = "Writer Performance Snapshot"
        verbose_name_plural = "Writer Performance Snapshots"
        ordering = ["-period_end"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "writer", "period_start", "period_end"],
                name="unique_snapshot_per_writer_period",
            ),
            models.CheckConstraint(
                condition=models.Q(period_end__gte=models.F("period_start")),
                name="snapshot_period_end_gte_start",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(average_rating__isnull=True) |
                    (
                        models.Q(average_rating__gte=Decimal("0.00")) &
                        models.Q(average_rating__lte=Decimal("5.00"))
                    )
                ),
                name="snapshot_avg_rating_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(completion_rate__gte=Decimal("0.0000")) &
                    models.Q(completion_rate__lte=Decimal("1.0000"))
                ),
                name="snapshot_completion_rate_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(lateness_rate__gte=Decimal("0.0000")) &
                    models.Q(lateness_rate__lte=Decimal("1.0000"))
                ),
                name="snapshot_lateness_rate_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(revision_rate__gte=Decimal("0.0000")) &
                    models.Q(revision_rate__lte=Decimal("1.0000"))
                ),
                name="snapshot_revision_rate_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(dispute_rate__gte=Decimal("0.0000")) &
                    models.Q(dispute_rate__lte=Decimal("1.0000"))
                ),
                name="snapshot_dispute_rate_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(cancellation_rate__gte=Decimal("0.0000")) &
                    models.Q(cancellation_rate__lte=Decimal("1.0000"))
                ),
                name="snapshot_cancellation_rate_range",
            ),
            # Composite score only when processed
            models.CheckConstraint(
                condition=(
                    models.Q(is_processed=False) |
                    models.Q(composite_score__isnull=False)
                ),
                name="snapshot_processed_has_score",
            ),
        ]
        indexes = [
            models.Index(
                fields=["writer", "period_end"],
                name="snapshot_writer_period_idx",
            ),
            models.Index(
                fields=["website", "period_end", "is_processed"],
                name="snapshot_site_processing_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterPerformanceSnapshot<{self.writer.id}> "
            f"{self.period_start} → {self.period_end}"
            f"{' ' if self.is_processed else ''}"
        )


# ════════════════════════════════════════════════════════════════════
# WriterPerformanceMetrics — weekly aggregation with ranking
# ════════════════════════════════════════════════════════════════════

class WriterPerformanceMetrics(models.Model):
    """
    Aggregated weekly metrics with ranking context.

    One row per writer per week. Created by performance_aggregator_service
    on a weekly Celery task. Updated in-place if the task re-runs
    for the same week (idempotent via get_or_create + update).

    DIFFERS FROM WriterPerformanceSnapshot
    ---------------------------------------
    Snapshot:
        Immutable after processing.
        Used for level progression (can be monthly or weekly).
        Always has composite_score when processed.

    Metrics:
        Always weekly.
        Updated in-place if re-computed.
        Includes percentile_rank against other writers this week.
        Used for dashboards, reward evaluation, admin reporting.

    RATE FIELDS
    -----------
    Stored as percentages (0.00–100.00), not proportions.
    This is intentional — metrics are display-ready, snapshots
    are computation-ready.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_metrics",
    )
    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="performance_metrics",
    )

    # ----------------------------------------------------------------
    # TIME WINDOW (always calendar week)
    # ----------------------------------------------------------------

    week_start = models.DateField(db_index=True)
    week_end = models.DateField()

    # ----------------------------------------------------------------
    # CORE METRICS (percentages — display-ready)
    # ----------------------------------------------------------------

    avg_rating = models.DecimalField(
        max_digits=4, decimal_places=2,
        default=Decimal("0.00"),
    )
    revision_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal("0.00"),
        help_text="% of completed orders that received revisions.",
    )
    dispute_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal("0.00"),
        help_text="% of completed orders that were disputed.",
    )
    lateness_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal("0.00"),
        help_text="% of completed orders delivered late.",
    )
    cancellation_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal("0.00"),
    )
    acceptance_to_completion_ratio = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal("0.00"),
        help_text="% of accepted orders that were completed.",
    )
    preferred_order_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal("0.00"),
        help_text="% of orders matching writer preferences.",
    )
    avg_turnaround_time = models.DurationField(
        null=True, blank=True,
        help_text="Mean time from assignment to submission this week.",
    )

    # ----------------------------------------------------------------
    # VOLUME
    # ----------------------------------------------------------------

    total_orders_completed = models.PositiveIntegerField(default=0)
    total_pages_completed = models.PositiveIntegerField(default=0)
    hvo_orders_completed = models.PositiveIntegerField(
        default=0,
        help_text="High-value orders completed this week.",
    )

    # ----------------------------------------------------------------
    # FINANCIALS
    # ----------------------------------------------------------------

    total_earnings = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
    )
    total_tips = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
    )
    total_bonuses = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
    )
    total_fines = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
    )
    total_profit_contribution = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal("0.00"),
        help_text="Client revenue minus writer cost for this week.",
    )

    # ----------------------------------------------------------------
    # RANKING (computed after all writers' metrics are aggregated)
    # ----------------------------------------------------------------

    composite_score = models.DecimalField(
        max_digits=6, decimal_places=2,
        default=Decimal("0.00"),
        help_text="Weighted performance score for this week.",
    )
    percentile_rank = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Writer outperforms this % of writers on this site this week. "
            "Range: 0.00–100.00."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Performance Metrics"
        verbose_name_plural = "Writer Performance Metrics"
        ordering = ["-week_start"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "writer", "week_start"],
                name="unique_metrics_per_writer_week",
            ),
            models.CheckConstraint(
                condition=models.Q(week_end__gte=models.F("week_start")),
                name="metrics_week_end_gte_start",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(avg_rating__gte=Decimal("0.00")) &
                    models.Q(avg_rating__lte=Decimal("5.00"))
                ),
                name="metrics_avg_rating_range",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(percentile_rank__gte=Decimal("0.00")) &
                    models.Q(percentile_rank__lte=Decimal("100.00"))
                ),
                name="metrics_percentile_rank_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    total_earnings__gte=Decimal("0.00")
                ),
                name="metrics_earnings_gte_0",
            ),
        ]
        indexes = [
            models.Index(
                fields=["writer", "week_start"],
                name="metrics_writer_week_idx",
            ),
            models.Index(
                fields=["website", "composite_score"],
                name="metrics_site_score_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterPerformanceMetrics<{self.writer.id}> "
            f"w/e {self.week_end}"
      )