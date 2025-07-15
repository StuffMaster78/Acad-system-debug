# writer_management.services.writer_metrics_service.py

from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Count, Avg, Sum, Q, F, ExpressionWrapper, DurationField
from django.utils.timezone import now

from writer_management.models.performance_snapshot import WriterPerformanceSnapshot
from writer_management.models.profile import WriterProfile
from orders.models import Order
from writer_management.models.payout import WriterPayment


class WriterMetricsService:
    @staticmethod
    def generate_snapshot(
        writer: WriterProfile, start: date, end: date
    ) -> WriterPerformanceSnapshot:
        """
        Calculates and stores a snapshot of performance metrics for a writer
        over a given date range.
        """

        orders = Order.objects.filter(
            assigned_writer=writer.user,
            created_at__date__gte=start,
            created_at__date__lte=end,
        )

        completed_orders = orders.filter(status="completed")
        cancelled_orders = orders.filter(status="cancelled")
        revised_orders = orders.filter(
            status__in=["revision_requested", "revision_completed"]
        )
        late_orders = orders.filter(due_at__lt=F("completed_at"))
        disputed_orders = orders.filter(dispute__isnull=False)
        preferred_orders = orders.filter(preferred_writer=True)
        hvo_orders = orders.filter(is_high_value=True)

        total_pages = completed_orders.aggregate(
            total_pages=Sum("num_pages")
        )["total_pages"] or 0

        turnaround_time = ExpressionWrapper(
            F("completed_at") - F("assigned_at"),
            output_field=DurationField()
        )

        avg_turnaround = completed_orders.annotate(
            turnaround=turnaround_time
        ).aggregate(
            avg_duration=Avg("turnaround")
        )["avg_duration"]

        avg_hours = (avg_turnaround.total_seconds() / 3600) if avg_turnaround else None

        total_orders = orders.count()
        completed_count = completed_orders.count()
        cancelled_count = cancelled_orders.count()
        revised_count = revised_orders.count()
        late_count = late_orders.count()
        disputed_count = disputed_orders.count()
        preferred_count = preferred_orders.count()
        hvo_count = hvo_orders.count()

        rating = completed_orders.aggregate(
            avg_rating=Avg("client_rating")
        )["avg_rating"]

        # Earnings & Profit
        payouts = WriterPayment.objects.filter(
            writer=writer,
            payment_date__date__gte=start,
            payment_date__date__lte=end,
        )

        earnings = payouts.aggregate(
            paid=Sum("amount"),
            tips=Sum("tips"),
            bonuses=Sum("bonuses")
        )

        amount_paid = earnings["paid"] or Decimal("0.00")
        tips = earnings["tips"] or Decimal("0.00")
        bonuses = earnings["bonuses"] or Decimal("0.00")

        client_revenue = completed_orders.aggregate(
            total_rev=Sum("total_price")
        )["total_rev"] or Decimal("0.00")

        profit_contrib = client_revenue - amount_paid

        # Rate calculations (avoid div by zero)
        completion_rate = (
            completed_count / total_orders if total_orders > 0 else 0
        )
        revision_rate = (
            revised_count / completed_count if completed_count > 0 else 0
        )
        lateness_rate = (
            late_count / completed_count if completed_count > 0 else 0
        )
        dispute_rate = (
            disputed_count / completed_count if completed_count > 0 else 0
        )
        preferred_rate = (
            preferred_count / total_orders if total_orders > 0 else 0
        )

        snapshot, _ = WriterPerformanceSnapshot.objects.update_or_create(
            writer=writer,
            website=writer.website,
            period_start=start,
            period_end=end,
            defaults={
                "total_orders": total_orders,
                "completed_orders": completed_count,
                "cancelled_orders": cancelled_count,
                "late_orders": late_count,
                "revised_orders": revised_count,
                "disputed_orders": disputed_count,
                "hvo_orders": hvo_count,
                "preferred_orders": preferred_count,
                "total_pages": total_pages,
                "amount_paid": amount_paid,
                "bonuses": bonuses,
                "tips": tips,
                "client_revenue": client_revenue,
                "profit_contribution": profit_contrib,
                "average_rating": rating or None,
                "average_turnaround_hours": avg_hours,
                "completion_rate": completion_rate,
                "revision_rate": revision_rate,
                "lateness_rate": lateness_rate,
                "dispute_rate": dispute_rate,
                "preferred_order_rate": preferred_rate,
                "is_cached": True,
                "generated_at": now(),
            }
        )

        return snapshot