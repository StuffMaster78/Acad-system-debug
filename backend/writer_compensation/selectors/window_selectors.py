from __future__ import annotations

from decimal import Decimal

from django.db.models import Count, OuterRef, Q, Sum

from writer_compensation.enums.compensation_enums import (
    EventStatus,
    WindowStatus,
)
from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.models.payment_window import PaymentWindow
from writer_compensation.models.payout_record import PayoutRecord


class WindowSelectors:

    @staticmethod
    def get_open_window(website) -> PaymentWindow | None:
        return (
            PaymentWindow.objects
            .filter(website=website, status=WindowStatus.OPEN)
            .order_by("-start_date")
            .first()
        )

    @staticmethod
    def get_window_by_id(window_id: int, website) -> PaymentWindow | None:
        return (
            PaymentWindow.objects
            .filter(pk=window_id, website=website)
            .first()
        )

    @staticmethod
    def get_all_windows(website):
        return (
            PaymentWindow.objects
            .filter(website=website)
            .order_by("-start_date")
        )

    @staticmethod
    def get_writer_events_for_window(
        writer,
        window: PaymentWindow,
    ) -> tuple:
        """
        Returns (queryset, totals_dict) for one writer in one window.
        Powers the per-writer admin detail view.
        """
        events = (
            CompensationEvent.objects
            .filter(writer=writer, payment_window=window)
            .select_related("created_by", "related_window")
            .order_by("created_at")
        )

        totals = events.aggregate(
            gross=Sum("amount", filter=Q(amount__gt=0)),
            deductions=Sum("amount", filter=Q(amount__lt=0)),
            net=Sum("amount"),
            count=Count("id"),
        )

        totals["gross"]      = totals["gross"]      or Decimal("0.00")
        totals["deductions"] = totals["deductions"] or Decimal("0.00")
        totals["net"]        = totals["net"]        or Decimal("0.00")
        totals["count"]      = totals["count"]      or 0

        return events, totals

    @staticmethod
    def get_writer_event_breakdown(writer, window: PaymentWindow):
        """
        Per-type subtotal for a writer in a window.
        Powers the breakdown footer in the admin detail view.
        """
        return (
            CompensationEvent.objects
            .filter(writer=writer, payment_window=window)
            .values("event_type")
            .annotate(subtotal=Sum("amount"))
            .order_by("event_type")
        )

    @staticmethod
    def get_window_summary(window: PaymentWindow):
        """
        Per-writer aggregate for a window.
        Powers the admin batch overview table.
        """
        return (
            CompensationEvent.objects
            .filter(payment_window=window)
            .values("writer_id")
            .annotate(
                gross=Sum("amount", filter=Q(amount__gt=0)),
                deductions=Sum("amount", filter=Q(amount__lt=0)),
                net=Sum("amount"),
                event_count=Count("id"),
            )
            .order_by("-net")
        )

    @staticmethod
    def has_pending_events(window: PaymentWindow) -> bool:
        """
        True if any events in this window
        are still PENDING_CONFIRMATION.
        """
        return CompensationEvent.objects.filter(
            payment_window=window,
            status=EventStatus.PENDING_CONFIRMATION,
        ).exists()

    @staticmethod
    def pending_event_count(window: PaymentWindow) -> int:
        return CompensationEvent.objects.filter(
            payment_window=window,
            status=EventStatus.PENDING_CONFIRMATION,
        ).count()