from __future__ import annotations

from dataclasses import asdict
from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.order_ops_permissions import (
    CanViewOrderOpsDashboard,
)
from orders.selectors.order_ops_selector import (
    OrderOpsSelector,
)


class OrderOpsDashboardSummaryView(GenericAPIView):
    """
    Return top-line operations dashboard counts for staff.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewOrderOpsDashboard,
    ]

    def get(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Return summary counts for operational queues.
        """
        user = cast(Any, request.user)
        counts = OrderOpsSelector.dashboard_counts(
            website=request.website,
        )

        return Response(
            asdict(counts),
            status=status.HTTP_200_OK,
        )


class OrderOpsQueueView(GenericAPIView):
    """
    Return a specific operations queue for staff.

    Supported queues:
        1. late
        2. critical
        3. awaiting_approval
        4. awaiting_acknowledgement
        5. pending_staffing
        6. preferred_writer_pending
        7. eligible_for_archive
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewOrderOpsDashboard,
    ]

    def get(
        self,
        request: Request,
        queue_key: str,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Return serialized queue rows for the requested key.
        """
        user = cast(Any, request.user)
        queryset = self._resolve_queue(
            website=request.website,
            queue_key=queue_key,
        )

        rows = [self._serialize_order(order=order) for order in queryset[:100]]

        return Response(
            {
                "queue_key": queue_key,
                "count": len(rows),
                "results": rows,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _resolve_queue(*, website: Any, queue_key: str):
        """
        Resolve dashboard queue queryset for the supplied key.
        """
        mapping = {
            "late": OrderOpsSelector.late_orders,
            "critical": OrderOpsSelector.critical_orders,
            "awaiting_approval": OrderOpsSelector.awaiting_approval,
            "awaiting_acknowledgement": (
                OrderOpsSelector.awaiting_acknowledgement
            ),
            "pending_staffing": OrderOpsSelector.pending_staffing,
            "preferred_writer_pending": (
                OrderOpsSelector.preferred_writer_pending
            ),
            "eligible_for_archive": (
                OrderOpsSelector.eligible_for_archive
            ),
        }

        resolver = mapping.get(queue_key)
        if resolver is None:
            raise ValueError(f"Unsupported queue_key: {queue_key}")

        return resolver(website=website)

    @staticmethod
    def _serialize_order(*, order) -> dict[str, Any]:
        """
        Serialize an operational queue row.
        """
        return {
            "id": order.pk,
            "topic": order.topic,
            "status": order.status,
            "payment_status": getattr(order, "payment_status", ""),
            "total_price": str(getattr(order, "total_price", "")),
            "amount_paid": str(getattr(order, "amount_paid", "")),
            "client_deadline": getattr(order, "client_deadline", None),
            "writer_deadline": getattr(order, "writer_deadline", None),
            "preferred_writer_status": getattr(
                order,
                "preferred_writer_status",
                "",
            ),
            "client_id": getattr(getattr(order, "client", None), "pk", None),
            "preferred_writer_id": getattr(
                getattr(order, "preferred_writer", None),
                "pk",
                None,
            ),
        }