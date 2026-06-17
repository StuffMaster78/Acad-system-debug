from __future__ import annotations

from typing import Any

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models.orders.order_cancellation_request import OrderCancellationRequest
from orders.api.permissions.staffing_permissions import IsStaffUser


class PendingCancellationQueueView(APIView):
    """
    GET /api/orders/cancellation-requests/pending/

    Returns all pending cancellation requests for the tenant, with
    enough order context for staff to review and action from the list.
    Staff-only.
    """

    permission_classes = [permissions.IsAuthenticated, IsStaffUser]

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        qs = (
            OrderCancellationRequest.objects
            .filter(
                website=user.website,
                status=OrderCancellationRequest.STATUS_PENDING,
            )
            .select_related(
                "order",
                "order__client",
                "requested_by",
            )
            .order_by("requested_at")
        )

        results = []
        for req in qs:
            order = req.order
            results.append({
                "id": req.pk,
                "order_id": order.pk,
                "order_topic": order.topic,
                "order_status": order.status,
                "client_id": getattr(order, "client_id", None),
                "client_deadline": str(order.client_deadline) if getattr(order, "client_deadline", None) else None,
                "reason": req.reason,
                "forfeiture_pct": str(req.forfeiture_pct),
                "forfeiture_amount": str(req.forfeiture_amount),
                "refund_amount": str(req.refund_amount),
                "requested_at": req.requested_at.isoformat(),
                "pre_request_status": req.pre_request_status,
            })

        return Response(results, status=status.HTTP_200_OK)
