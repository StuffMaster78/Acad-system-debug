from __future__ import annotations

from typing import Any, TypedDict, cast, NotRequired

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.api.serializers.cancellation.order_cancellation_serializer import (
    OrderCancelActionSerializer,
)
from orders.models.orders.order import Order
from orders.services.order_cancellation_service import (
    OrderCancellationService,
)
from orders.api.permissions.order_cancellation_permissions import (
    CanCancelOrder,
)


class OrderCancellationData(TypedDict):
    reason: str
    refund_destination: str
    notes: NotRequired[str]


class OrderCancellationView(APIView):
    """
    Cancel a single order.
    """

    permission_classes = [permissions.IsAuthenticated, CanCancelOrder]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        order = get_object_or_404(
            Order.objects.select_related("website", "client"),
            pk=order_id,
            website=request.user.website,
        )

        self.check_object_permissions(request, order)

        serializer = OrderCancelActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(OrderCancellationData, serializer.validated_data)

        cancelled_order = OrderCancellationService.cancel_order(
            order=order,
            cancelled_by=request.user,
            reason=data["reason"],
            refund_destination=data["refund_destination"],
            notes=data.get("notes", ""),
            triggered_by=request.user,
        )

        cancelled_at = getattr(cancelled_order, "cancelled_at", None)

        return Response(
            {
                "detail": "Order cancelled successfully.",
                "order_id": cancelled_order.pk,
                "status": cancelled_order.status,
                "cancelled_at": (
                    cancelled_at.isoformat()
                    if cancelled_at is not None
                    else None
                ),
                "refund_destination": data["refund_destination"],
            },
            status=status.HTTP_200_OK,
        )