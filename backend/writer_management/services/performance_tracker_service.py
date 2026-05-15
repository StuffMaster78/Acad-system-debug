"""
Real-time updates to WriterPerformance counters after order events.

ARCHITECTURE
------------
WriterPerformance is the canonical source for lifetime writer metrics:
- completed_orders, total_orders, pending_orders
- late_deliveries, on_time_deliveries, cancelled_orders
- revision_count, disputed_orders
- average_rating, total_ratings (using Welford's algorithm)
- total_earnings, total_tips, total_bonuses, total_fines (synced from writer_compensation)

This service is called by order signals/webhooks to increment/decrement counters
using atomic F() expressions to avoid race conditions.

SINGLE RESPONSIBILITY: Update WriterPerformance after lifecycle events.

ENTRY POINTS
------------
- order_assigned(writer, order)       — pending_orders += 1
- order_completed(writer, order)      — completed_orders += 1, pending_orders -= 1
- order_cancelled(writer, order)      — cancelled_orders += 1, pending_orders -= 1
- order_delivered_late(writer, order) — late_deliveries += 1
- order_delivered_on_time(writer)     — on_time_deliveries += 1
- order_disputed(writer, order)       — disputed_orders += 1
- revision_requested(writer, order)   — revision_count += 1
- rating_received(writer, rating)     — updates average_rating (Welford's)
- sync_financials(writer, ...)        — sets earnings/tips/bonuses/fines (replace, not increment)

ALGORITHM: Welford's Online Mean
---------------------------------
For incremental rating average without storing all ratings:
    new_avg = old_avg + (new_value - old_avg) / new_count

Prevents: Recomputing avg from millions of ratings on every new rating.
Requires: select_for_update lock to prevent concurrent corruption.
"""

import logging
from decimal import Decimal

from django.db import models, transaction

logger = logging.getLogger(__name__)


class PerformanceTrackerService:

    @staticmethod
    @transaction.atomic
    def order_completed(writer_profile, order=None) -> None:
        """
        Writer completed an order successfully.
        Increments: completed_orders, total_orders.
        Decrements: pending_orders.
        """
        from writer_management.models.writer_performance import WriterPerformance

        WriterPerformance.objects.filter(
            writer=writer_profile,
        ).update(
            completed_orders=models.F("completed_orders") + 1,
            total_orders=models.F("total_orders") + 1,
            pending_orders=models.F("pending_orders") - 1,
        )

        logger.debug(
            "PerformanceTracker.order_completed: writer=%s",
            writer_profile.registration_id,
        )

    @staticmethod
    @transaction.atomic
    def order_assigned(writer_profile, order=None) -> None:
        """
        Order assigned to writer — increments pending.
        Called at assignment time, before completion.
        """
        from writer_management.models.writer_performance import WriterPerformance

        WriterPerformance.objects.filter(
            writer=writer_profile,
        ).update(
            pending_orders=models.F("pending_orders") + 1,
        )

    @staticmethod
    @transaction.atomic
    def order_cancelled(writer_profile, order=None) -> None:
        """
        Order cancelled after assignment.
        Increments: cancelled_orders.
        Decrements: pending_orders.
        """
        from writer_management.models.writer_performance import WriterPerformance

        WriterPerformance.objects.filter(
            writer=writer_profile,
        ).update(
            cancelled_orders=models.F("cancelled_orders") + 1,
            pending_orders=models.F("pending_orders") - 1,
        )

        logger.debug(
            "PerformanceTracker.order_cancelled: writer=%s",
            writer_profile.registration_id,
        )

    @staticmethod
    @transaction.atomic
    def order_delivered_late(writer_profile, order=None) -> None:
        """
        Order submitted past the writer's internal deadline.
        Increments: late_deliveries.
        """
        from writer_management.models.writer_performance import WriterPerformance

        WriterPerformance.objects.filter(
            writer=writer_profile,
        ).update(
            late_deliveries=models.F("late_deliveries") + 1,
        )

    @staticmethod
    @transaction.atomic
    def order_delivered_on_time(writer_profile, order=None) -> None:
        """
        Order submitted on or before the writer's internal deadline.
        Increments: on_time_deliveries.
        """
        from writer_management.models.writer_performance import WriterPerformance

        WriterPerformance.objects.filter(
            writer=writer_profile,
        ).update(
            on_time_deliveries=models.F("on_time_deliveries") + 1,
        )

    @staticmethod
    @transaction.atomic
    def order_disputed(writer_profile, order=None) -> None:
        """Order was disputed by client."""
        from writer_management.models.writer_performance import WriterPerformance

        WriterPerformance.objects.filter(
            writer=writer_profile,
        ).update(
            disputed_orders=models.F("disputed_orders") + 1,
        )

    @staticmethod
    @transaction.atomic
    def revision_requested(writer_profile, order=None) -> None:
        """Revision requested on a completed order."""
        from writer_management.models.writer_performance import WriterPerformance

        WriterPerformance.objects.filter(
            writer=writer_profile,
        ).update(
            revision_count=models.F("revision_count") + 1,
        )

    @staticmethod
    @transaction.atomic
    def rating_received(
        writer_profile,
        rating_value: int,
    ) -> None:
        """
        New rating received from a client.

        Updates average_rating using Welford's online algorithm:
            new_avg = old_avg + (new_value - old_avg) / new_count

        This avoids loading all ratings to recompute the average.
        Requires a select_for_update to prevent concurrent rating
        race conditions corrupting the average.

        Args:
            writer_profile: WriterProfile instance.
            rating_value:   Integer 1–5.
        """
        from writer_management.models.writer_performance import WriterPerformance

        if rating_value not in range(1, 6):
            raise ValueError(
                f"rating_value must be 1–5, got {rating_value}."
            )

        # select_for_update prevents concurrent Welford corruption
        try:
            perf = WriterPerformance.objects.select_for_update().get(
                writer=writer_profile,
            )
        except WriterPerformance.DoesNotExist:
            logger.error(
                "WriterPerformance row missing for writer=%s. "
                "Cannot update average_rating.",
                writer_profile.registration_id,
            )
            return

        new_count = perf.total_ratings + 1
        new_avg = perf.average_rating + (
            (Decimal(str(rating_value)) - perf.average_rating) /
            Decimal(str(new_count))
        )
        # Round to 2 decimal places
        new_avg = new_avg.quantize(Decimal("0.01"))

        perf.average_rating = new_avg
        perf.total_ratings = new_count
        perf.save(update_fields=["average_rating", "total_ratings", "updated_at"])

        logger.debug(
            "PerformanceTracker.rating_received: writer=%s "
            "new_rating=%d new_avg=%s new_count=%d",
            writer_profile.registration_id,
            rating_value,
            new_avg,
            new_count,
        )

    @staticmethod
    @transaction.atomic
    def sync_financials(
        writer_profile,
        total_earnings: Decimal,
        total_tips: Decimal,
        total_bonuses: Decimal,
        total_fines: Decimal,
    ) -> None:
        """
        Sync financial mirrors from writer_compensation.

        Called by writer_metrics_snapshot_service during weekly
        reconciliation. Replaces (not increments) the financial fields.

        Args:
            writer_profile: WriterProfile instance.
            total_earnings: Gross lifetime earnings from writer_compensation.
            total_tips:     Lifetime tips from tips app.
            total_bonuses:  Lifetime bonuses.
            total_fines:    Lifetime fines/penalties.
        """
        from writer_management.models.writer_performance import WriterPerformance

        WriterPerformance.objects.filter(
            writer=writer_profile,
        ).update(
            total_earnings=total_earnings,
            total_tips_received=total_tips,
            total_bonuses=total_bonuses,
            total_fines=total_fines,
        )

        logger.info(
            "PerformanceTracker.sync_financials: writer=%s "
            "earnings=%s tips=%s bonuses=%s fines=%s",
            writer_profile.registration_id,
            total_earnings,
            total_tips,
            total_bonuses,
            total_fines,
        )

    @staticmethod
    def get_or_create_performance(writer_profile, website):
        """
        Fetch or create WriterPerformance for a writer.
        Used by bootstrap signal and admin tools.
        """
        from writer_management.models.writer_performance import WriterPerformance

        perf, created = WriterPerformance.objects.get_or_create(
            writer=writer_profile,
            defaults={"website": website},
        )
        if created:
            logger.info(
                "WriterPerformance created for writer=%s",
                writer_profile.registration_id,
            )
        return perf