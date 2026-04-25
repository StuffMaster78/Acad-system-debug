from __future__ import annotations

from django.db.models import QuerySet

from orders.models.adjustments.order_adjustment_request import (
    OrderAdjustmentRequest,
)
from orders.models.orders.constants import (
    ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE,
    ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT,
    ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED,
    ORDER_ADJUSTMENT_STATUS_COUNTER_FUNDED_FINAL,
    ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING,
    ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
)


class OrderAdjustmentSelector:
    """
    Read-side helpers for order adjustment requests.
    Reduces the amount of logic in views and serializers, and
    provides a single place to update if the underlying data model changes.
    """

    @staticmethod
    def base_queryset(
        *, website
    ) -> QuerySet:
        """
        Base tenant-scoped queryset for order adjustment requests.
        """
        return OrderAdjustmentRequest.objects.filter(
            website=website
        ).select_related(
            "order",
            "requested_by",
            "reviewed_by",
            "current_proposal",
            "accepred_proposal",
        )


    @staticmethod
    def pending_client_response(
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Order adjustment requests that are pending a response from the client.
        """
        return OrderAdjustmentSelector.base_queryset(
            website=website
        ).filter(
            status=ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE
        )


    @staticmethod
    def client_countered(
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Order adjustment requests that have been countered by the client.
        """
        return OrderAdjustmentSelector.base_queryset(
            website=website
        ).filter(
            status=ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED
        )
    
    @staticmethod
    def funding_pending(
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Order adjustment requests that are pending funding.
        """
        return OrderAdjustmentSelector.base_queryset(
            website=website
        ).filter(
            status=ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING
        )


    @staticmethod
    def counter_funded_final(
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Order adjustment requests that have been counter funded and are in their final state.
        """
        return OrderAdjustmentSelector.base_queryset(
            website=website
        ).filter(
            status=ORDER_ADJUSTMENT_STATUS_COUNTER_FUNDED_FINAL
        )
    
    @staticmethod
    def open_scope_increments(
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Order adjustment requests that are scope increments and are still open.
        """
        return OrderAdjustmentSelector.base_queryset(
            website=website
        ).filter(
            kind=ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT,
            applied_at__isnull=True,
        ).exclude(
            status__in=[
                ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
                ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED,
                ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING,
                ORDER_ADJUSTMENT_STATUS_COUNTER_FUNDED_FINAL,
            ]
        )


    @staticmethod
    def open_extra_services(
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Order adjustment requests that are extra services and are still open.
        """
        return OrderAdjustmentSelector.base_queryset(
            website=website
        ).filter(
            kind=ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE,
            applied_at__isnull=True,
        ).exclude(
            status__in=[
                ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
                ORDER_ADJUSTMENT_STATUS_CLIENT_COUNTERED,
                ORDER_ADJUSTMENT_STATUS_FUNDING_PENDING,
                ORDER_ADJUSTMENT_STATUS_COUNTER_FUNDED_FINAL,
            ]
        )


    @staticmethod
    def post_counter_escalations(
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Order adjustment requests that have been escalated after being countered.
        """
        return OrderAdjustmentSelector.base_queryset(
            website=website
        ).filter(
            escalated_after_counter=True,
            resolved_at__isnull=True,
        )