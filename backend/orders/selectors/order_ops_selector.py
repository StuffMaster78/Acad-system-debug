from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db.models import QuerySet
from django.utils import timezone

from orders.models.orders.enums import OrderStatus, PreferredWriterStatus
from orders.models import Order


@dataclass(frozen=True)
class OrderOpsDashboardCounts:
    """
    Hold top-line operational dashboard counts.
    """

    late_orders: int
    critical_orders: int
    awaiting_approval: int
    awaiting_acknowledgement: int
    pending_staffing: int
    preferred_writer_pending: int
    eligible_for_archive: int


class OrderOpsSelector:
    """
    Provide read-side operational dashboard queries for orders.

    Responsibilities:
        1. Return queue querysets for operations dashboards.
        2. Return top-line queue counts.
        3. Keep dashboard query logic out of views.
    """

    @staticmethod
    def late_orders(*, website: Any) -> QuerySet[Order]:
        """
        Return in-progress orders that crossed writer deadline.
        """
        return Order.objects.filter(
            website=website,
            status=OrderStatus.IN_PROGRESS,
            writer_deadline__lt=timezone.now(),
        ).select_related("client", "preferred_writer")

    @staticmethod
    def critical_orders(*, website: Any) -> QuerySet[Order]:
        """
        Return in-progress orders nearing writer deadline.

        Notes:
            Uses the current is_urgent flag as a first practical slice.
            You can later tighten this using a dedicated monitoring
            threshold selector if needed.
        """
        return Order.objects.filter(
            website=website,
            status=OrderStatus.IN_PROGRESS,
            is_urgent=True,
        ).select_related("client", "preferred_writer")

    @staticmethod
    def awaiting_approval(*, website: Any) -> QuerySet[Order]:
        """
        Return submitted orders still awaiting approval.
        """
        return Order.objects.filter(
            website=website,
            status=OrderStatus.SUBMITTED,
            approved_at__isnull=True,
        ).select_related("client")

    @staticmethod
    def awaiting_acknowledgement(*, website: Any) -> QuerySet[Order]:
        """
        Return active orders not yet acknowledged by the writer.
        """
        return Order.objects.filter(
            website=website,
            status=OrderStatus.IN_PROGRESS,
            last_writer_acknowledged_at__isnull=True,
        ).select_related("client", "preferred_writer")

    @staticmethod
    def pending_staffing(*, website: Any) -> QuerySet[Order]:
        """
        Return orders ready for staffing.
        """
        return Order.objects.filter(
            website=website,
            status=OrderStatus.READY_FOR_STAFFING,
        ).select_related("client", "preferred_writer")

    @staticmethod
    def preferred_writer_pending(*, website: Any) -> QuerySet[Order]:
        """
        Return staffing-ready orders still waiting on preferred writer flow.
        """
        return Order.objects.filter(
            website=website,
            status=OrderStatus.READY_FOR_STAFFING,
            preferred_writer_status=PreferredWriterStatus.INVITED,
        ).select_related("client", "preferred_writer")

    @staticmethod
    def eligible_for_archive(*, website: Any) -> QuerySet[Order]:
        """
        Return completed orders old enough to be archived.

        Notes:
            This uses a simple completed-and-not-archived queue for ops
            visibility. The archival service still owns the final
            eligibility decision.
        """
        return Order.objects.filter(
            website=website,
            status=OrderStatus.COMPLETED,
            archived_at__isnull=True,
        ).select_related("client")

    @classmethod
    def dashboard_counts(
        cls,
        *,
        website: Any,
    ) -> OrderOpsDashboardCounts:
        """
        Return top-line operational dashboard counts.
        """
        return OrderOpsDashboardCounts(
            late_orders=cls.late_orders(website=website).count(),
            critical_orders=cls.critical_orders(website=website).count(),
            awaiting_approval=cls.awaiting_approval(
                website=website
            ).count(),
            awaiting_acknowledgement=cls.awaiting_acknowledgement(
                website=website
            ).count(),
            pending_staffing=cls.pending_staffing(
                website=website
            ).count(),
            preferred_writer_pending=cls.preferred_writer_pending(
                website=website
            ).count(),
            eligible_for_archive=cls.eligible_for_archive(
                website=website
            ).count(),
        )