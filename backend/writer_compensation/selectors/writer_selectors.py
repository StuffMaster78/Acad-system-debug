from __future__ import annotations

from decimal import Decimal

from django.db.models import Count, Q, Sum

from writer_compensation.enums.compensation_enums import (
    CycleChangeStatus,
    EventStatus,
    WindowStatus,
)
from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.models.cycle_change_request import PaymentWindowChangeRequest
from writer_compensation.models.payment_window import PaymentWindow
from writer_compensation.models.writer_payout_preference import WriterPayoutPreference
from writer_compensation.selectors.window_selectors import WindowSelectors


class WriterSelectors:

    @staticmethod
    def get_writer_events(writer, website, filters: dict | None = None):
        qs = (
            CompensationEvent.objects
            .filter(writer=writer, website=website)
            .select_related("payment_window", "related_window")
            .order_by("-created_at")
        )

        if filters:
            if filters.get("event_type"):
                qs = qs.filter(event_type=filters["event_type"])
            if filters.get("status"):
                qs = qs.filter(status=filters["status"])
            if filters.get("window_id"):
                qs = qs.filter(payment_window_id=filters["window_id"])
            if filters.get("from_date"):
                qs = qs.filter(created_at__date__gte=filters["from_date"])
            if filters.get("to_date"):
                qs = qs.filter(created_at__date__lte=filters["to_date"])

        return qs

    @staticmethod
    def get_writer_lifetime_summary(writer, website) -> dict:
        qs = CompensationEvent.objects.filter(writer=writer, website=website)
        result = qs.aggregate(
            total_earned=Sum("amount", filter=Q(amount__gt=0)),
            total_deductions=Sum("amount", filter=Q(amount__lt=0)),
            total_net=Sum("amount"),
            total_paid=Sum(
                "amount",
                filter=Q(status=EventStatus.PAID, amount__gt=0),
            ),
        )
        for key in result:
            result[key] = result[key] or Decimal("0.00")
        return result

    @staticmethod
    def get_writer_current_window_status(writer, website) -> dict:
        open_window = WindowSelectors.get_open_window(website)
        processing_window = (
            PaymentWindow.objects
            .filter(website=website, status=WindowStatus.PROCESSING)
            .first()
        )
        current_window = processing_window or open_window

        if not current_window:
            return {
                "window": None,
                "net": Decimal("0.00"),
                "count": 0,
                "is_processing": False,
            }

        totals = CompensationEvent.objects.filter(
            writer=writer,
            payment_window=current_window,
        ).aggregate(net=Sum("amount"), count=Count("id"))

        return {
            "window": current_window,
            "net": totals["net"] or Decimal("0.00"),
            "count": totals["count"] or 0,
            "is_processing": current_window.status == WindowStatus.PROCESSING,
        }

    @staticmethod
    def get_writer_payout_preference(writer, website) -> WriterPayoutPreference | None:
        return WriterPayoutPreference.objects.filter(
            writer=writer,
            website=website,
        ).first()

    @staticmethod
    def get_pending_cycle_change_request(
        writer,
        website,
    ) -> PaymentWindowChangeRequest | None:
        return PaymentWindowChangeRequest.objects.filter(
            writer=writer,
            website=website,
            status=CycleChangeStatus.PENDING,
        ).first()