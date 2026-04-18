from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from orders.constants import (
    UnpaidOrderDispatchStatus,
)
from orders.models.legacy_models.unpaid_order_message_dispatch import (
    UnpaidOrderMessageDispatch,
)
from websites.models.websites import Website


class UnpaidOrderMessageDispatchSelector:
    """
    Read only queries for unpaid order reminder dispatches.
    """

    @staticmethod
    def get_due_pending_dispatches(
        *,
        website: Website | None = None,
    ) -> QuerySet[UnpaidOrderMessageDispatch]:
        """
        Return pending dispatches due for processing.
        """
        queryset = UnpaidOrderMessageDispatch.objects.select_related(
            "order",
            "order__website",
            "client",
            "unpaid_order_message",
        ).filter(
            status=UnpaidOrderDispatchStatus.PENDING,
            scheduled_for__lte=timezone.now(),
        )

        if website is not None:
            queryset = queryset.filter(website=website)

        return queryset.order_by("scheduled_for", "id")

    @staticmethod
    def get_pending_dispatches_for_order(
        *,
        order,
    ) -> QuerySet[UnpaidOrderMessageDispatch]:
        """
        Return unsent pending dispatches for an order.
        """
        return UnpaidOrderMessageDispatch.objects.filter(
            order=order,
            status=UnpaidOrderDispatchStatus.PENDING,
        ).order_by("scheduled_for", "id")