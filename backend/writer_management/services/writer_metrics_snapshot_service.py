"""
writer_management/services/writer_metrics_snapshot_service.py

Creates WriterPerformanceSnapshot records for a given period.

RESPONSIBILITY
--------------
Reads raw order and performance data for a writer over a period,
computes all rate metrics, creates the snapshot row, then hands
off to CompositeScoreService to compute the composite score.

CALLED BY
---------
performance_aggregator_service — which coordinates the full
weekly/monthly pipeline across all writers on a site.

Never called directly from views or signals.

PERIOD CONVENTIONS
------------------
weekly:  Monday 00:00 → Sunday 23:59 UTC
monthly: First day of month 00:00 → Last day 23:59 UTC

All datetime comparisons use UTC. Writer timezone is not
relevant for period boundaries.

DATA SOURCES
------------
This service reads from:
    orders.Order         — completed, cancelled, disputed, late counts
    reviews_system       — ratings for the period
    writer_compensation  — earnings for the period

It writes to:
    WriterPerformanceSnapshot

IDEMPOTENCY
-----------
If a snapshot already exists for (writer, period_start, period_end),
the service updates it in place rather than creating a duplicate.
This makes the service safe to re-run if a task fails mid-way.
"""

import logging
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from django.db import models
from django.db import transaction
from django.utils.timezone import datetime, make_aware

from writer_management.models.writer_performance import WriterPerformanceSnapshot
from writer_management.services.composite_score_service import (
    CompositeScoreService,
)

logger = logging.getLogger(__name__)


class WriterMetricsSnapshotService:

    @staticmethod
    @transaction.atomic
    def create_or_update(
        writer_profile,
        website,
        period_start: date,
        period_end: date,
    ) -> WriterPerformanceSnapshot:
        """
        Create or update a WriterPerformanceSnapshot for a period.

        Args:
            writer_profile: WriterProfile instance.
            website:        Website instance.
            period_start:   First day of the period (inclusive).
            period_end:     Last day of the period (inclusive).

        Returns:
            WriterPerformanceSnapshot — processed (composite_score set).
        """
        # Convert date boundaries to datetime for ORM queries
        start_dt = make_aware(datetime.combine(period_start, datetime.min.time()))
        end_dt   = make_aware(datetime.combine(period_end,   datetime.max.time()))

        # Gather raw counts from orders
        counts = WriterMetricsSnapshotService._gather_order_counts(
            writer_profile, start_dt, end_dt
        )

        # Gather financials
        financials = WriterMetricsSnapshotService._gather_financials(
            writer_profile, start_dt, end_dt
        )

        # Gather ratings
        avg_rating = WriterMetricsSnapshotService._gather_avg_rating(
            writer_profile, start_dt, end_dt
        )

        # Compute rate metrics
        rates = WriterMetricsSnapshotService._compute_rates(counts)

        # Compute average turnaround
        avg_turnaround = WriterMetricsSnapshotService._compute_avg_turnaround(
            writer_profile, start_dt, end_dt
        )

        # Upsert snapshot
        snapshot, created = WriterPerformanceSnapshot.objects.update_or_create(
            writer=writer_profile,
            website=website,
            period_start=period_start,
            period_end=period_end,
            defaults={
                # Volume
                "total_orders":      counts["total"],
                "completed_orders":  counts["completed"],
                "cancelled_orders":  counts["cancelled"],
                "late_orders":       counts["late"],
                "revised_orders":    counts["revised"],
                "disputed_orders":   counts["disputed"],
                "hvo_orders":        counts["hvo"],
                "total_pages":       counts["pages"],
                "preferred_orders":  counts["preferred"],
                # Rates (proportions)
                "completion_rate":   rates["completion"],
                "lateness_rate":     rates["lateness"],
                "revision_rate":     rates["revision"],
                "dispute_rate":      rates["dispute"],
                "cancellation_rate": rates["cancellation"],
                "preferred_order_rate": rates["preferred"],
                "average_turnaround_hours": avg_turnaround,
                # Financials
                "amount_paid":          financials["earnings"],
                "bonuses":              financials["bonuses"],
                "tips":                 financials["tips"],
                "client_revenue":       financials["client_revenue"],
                "profit_contribution":  financials["profit"],
                # Rating
                "average_rating": avg_rating,
                # Reset processing state on update
                "is_processed": False,
            },
        )

        action = "Created" if created else "Updated"
        logger.info(
            "%s WriterPerformanceSnapshot: writer=%s period=%s→%s",
            action,
            writer_profile.registration_id,
            period_start,
            period_end,
        )

        # Compute and save composite score
        CompositeScoreService.compute_and_save(snapshot)

        return snapshot

    # ----------------------------------------------------------------
    # DATA GATHERING
    # ----------------------------------------------------------------

    @staticmethod
    def _gather_order_counts(writer_profile, start_dt, end_dt) -> dict:
        """
        Count order events for a writer in the period.
        Queries the orders app directly.
        """
        try:
            from orders.models.orders import Order

            base_qs = Order.objects.filter(
                assigned_writer=writer_profile,
            )

            # Orders completed in this period
            completed = base_qs.filter(
                status="completed",
                completed_at__range=(start_dt, end_dt),
            )

            total     = completed.count() + base_qs.filter(
                status="cancelled",
                cancelled_at__range=(start_dt, end_dt),
            ).count()

            completed_count   = completed.count()
            cancelled_count   = base_qs.filter(
                status="cancelled",
                cancelled_at__range=(start_dt, end_dt),
            ).count()
            late_count        = completed.filter(is_late=True).count()
            revised_count     = completed.filter(revision_count__gt=0).count()
            disputed_count    = completed.filter(is_disputed=True).count()
            hvo_count         = completed.filter(is_high_value=True).count()
            pages             = completed.aggregate(
                total=models.Sum("number_of_pages")
            )["total"] or 0
            preferred_count   = completed.filter(
                subject__in=writer_profile.capacity.preferred_subjects.all()
            ).count() if hasattr(writer_profile, "capacity") else 0

        except Exception as exc:
            logger.exception(
                "Failed to gather order counts for writer=%s: %s",
                writer_profile.registration_id,
                exc,
            )
            # Return zeroes — snapshot will reflect no activity
            return {
                "total": 0, "completed": 0, "cancelled": 0,
                "late": 0, "revised": 0, "disputed": 0,
                "hvo": 0, "pages": 0, "preferred": 0,
            }

        return {
            "total":     total,
            "completed": completed_count,
            "cancelled": cancelled_count,
            "late":      late_count,
            "revised":   revised_count,
            "disputed":  disputed_count,
            "hvo":       hvo_count,
            "pages":     pages,
            "preferred": preferred_count,
        }

    @staticmethod
    def _gather_financials(writer_profile, start_dt, end_dt) -> dict:
        """Gather financial data from writer_compensation."""
        try:
            from writer_compensation.services.earnings_query_service import (
                EarningsQueryService,
            )
            return EarningsQueryService.get_period_totals(
                website=website,
                start_date=start_dt,
                end_date=end_dt,
                status=status,
            )
        except ImportError:
            logger.warning(
                "writer_compensation not available — "
                "financial data will be zero for writer=%s",
                writer_profile.registration_id,
            )
        except Exception as exc:
            logger.exception(
                "Failed to gather financials for writer=%s: %s",
                writer_profile.registration_id,
                exc,
            )
        return {
            "earnings": Decimal("0.00"),
            "bonuses":  Decimal("0.00"),
            "tips":     Decimal("0.00"),
            "client_revenue": Decimal("0.00"),
            "profit":   Decimal("0.00"),
        }

    @staticmethod
    def _gather_avg_rating(
        writer_profile, start_dt, end_dt
    ) -> Decimal | None:
        """Average rating from reviews_system for the period."""
        try:
            from reviews_system.models.writer_review import WriterRating 
            from django.db.models import Avg

            result = WriterRating.objects.filter(
                writer=writer_profile,
                created_at__range=(start_dt, end_dt),
            ).aggregate(avg=Avg("rating"))

            avg = result.get("avg")
            if avg is None:
                return None
            return Decimal(str(avg)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except ImportError:
            return None
        except Exception as exc:
            logger.exception(
                "Failed to gather ratings for writer=%s: %s",
                writer_profile.registration_id,
                exc,
            )
            return None

    @staticmethod
    def _compute_avg_turnaround(
        writer_profile, start_dt, end_dt
    ) -> Decimal | None:
        """
        Mean hours from assignment to submission for the period.
        Returns None if no completed orders.
        """
        try:
            from orders.models.orders import Order
            from django.db.models import Avg, F, ExpressionWrapper, fields

            result = Order.objects.filter(
                assigned_writer=writer_profile,
                status="completed",
                completed_at__range=(start_dt, end_dt),
                assigned_at__isnull=False,
            ).annotate(
                turnaround=ExpressionWrapper(
                    F("completed_at") - F("assigned_at"),
                    output_field=fields.DurationField(),
                )
            ).aggregate(avg_turnaround=Avg("turnaround"))

            duration = result.get("avg_turnaround")
            if duration is None:
                return None
            hours = Decimal(str(duration.total_seconds() / 3600))
            return hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        except Exception as exc:
            logger.exception(
                "Failed to compute turnaround for writer=%s: %s",
                writer_profile.registration_id,
                exc,
            )
            return None

    @staticmethod
    def _compute_rates(counts: dict) -> dict:
        """
        Compute proportion rates from raw counts.
        All outputs are Decimal in range 0.0000–1.0000.
        """
        completed   = Decimal(str(counts["completed"]))
        total       = Decimal(str(counts["total"]))
        late        = Decimal(str(counts["late"]))
        revised     = Decimal(str(counts["revised"]))
        disputed    = Decimal(str(counts["disputed"]))
        cancelled   = Decimal(str(counts["cancelled"]))
        preferred   = Decimal(str(counts["preferred"]))

        def safe_rate(numerator, denominator) -> Decimal:
            if denominator == 0:
                return Decimal("0.0000")
            return (numerator / denominator).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            )

        return {
            "completion":   safe_rate(completed, total),
            "lateness":     safe_rate(late,      completed),
            "revision":     safe_rate(revised,   completed),
            "dispute":      safe_rate(disputed,  completed),
            "cancellation": safe_rate(cancelled, total),
            "preferred":    safe_rate(preferred, completed),
        }