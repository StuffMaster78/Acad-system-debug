from __future__ import annotations
 
from decimal import Decimal
 
from django.db.models import Count, OuterRef, Q, Subquery, Sum
 
from writer_compensation.enums.compensation_enums import (
    EventStatus,
    PayoutItemStatus,
    WindowStatus
)

from writer_compensation.models.compensation_event import (
    CompensationEvent,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)
from writer_compensation.models.cycle_change_request import (
    PaymentWindowChangeRequest,
)
from writer_compensation.selectors.payout_selectors import (
    PayoutSelectors,
)


class AdminSelectors:
 
    @staticmethod
    def get_held_items_site_wide(website):
        return PayoutSelectors.get_held_items_for_site(website)
 
    @staticmethod
    def get_failed_event_count(website) -> int:
        """Events that could not be confirmed — for admin alert badge."""
        return CompensationEvent.objects.filter(
            website=website,
            status=EventStatus.HELD,
        ).count()
 
    @staticmethod
    def get_top_earners(window: PaymentWindow, limit: int = 10):
        return (
            CompensationEvent.objects
            .filter(window=window, amount__gt=0)
            .values("writer_id")
            .annotate(total=Sum("amount"))
            .order_by("-total")[:limit]
        )
 
    @staticmethod
    def get_all_cycle_change_requests(website):
        from writer_compensation.enums.compensation_enums import CycleChangeStatus
        return (
            PaymentWindowChangeRequest.objects
            .filter(website=website, status=CycleChangeStatus.PENDING)
            .select_related("writer")
            .order_by("created_at")
        )
 
    @staticmethod
    def get_window_health(window: PaymentWindow) -> dict:
        """
        Snapshot of a window's state for admin overview.
        Returns counts useful for the admin UI warning badges.
        """
        events = CompensationEvent.objects.filter(window=window)
        batch  = PayoutSelectors.get_batch_for_window(window)
        counts = PayoutSelectors.get_batch_record_counts(batch) if batch else {}
 
        return {
            "pending_events":    events.filter(status=EventStatus.PENDING).count(),
            "confirmed_events":  events.filter(status=EventStatus.CONFIRMED).count(),
            "paid_events":       events.filter(status=EventStatus.PAID).count(),
            "payout_pending":    counts.get("pending",   0),
            "payout_confirmed":  counts.get("confirmed", 0),
            "payout_paid":       counts.get("paid",      0),
            "payout_held":       counts.get("held",      0),
        }