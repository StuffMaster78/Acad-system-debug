from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order
from orders.models.adjustments.order_adjustment_request import OrderAdjustmentRequest
from orders.models.orders.constants import ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE
from orders.models.orders.enums import OrderAdjustmentType, OrderScopeUnitType
from orders.services.order_notification_service import OrderNotificationService
from core.utils.request_context import resolve_request_website


class DeadlineExtensionSerializer(serializers.Serializer):
    requested_deadline = serializers.DateTimeField()
    reason = serializers.CharField(max_length=1000)
    writer_justification = serializers.CharField(
        required=False, allow_blank=True, default=""
    )


class CreateDeadlineExtensionView(APIView):
    """
    POST /api/v1/orders/orders/<order_id>/adjustments/deadline-extension/

    Writer requests an extension to the writer_deadline.
    No payment is involved — the client (or staff) simply accepts or rejects.

    On acceptance, staff should manually update order.writer_deadline.
    The requested new deadline is stored in metadata.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, order_id: int, *args: Any, **kwargs: Any) -> Response:
        serializer = DeadlineExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = cast(Any, request.user)
        website = resolve_request_website(request)

        order = get_object_or_404(
            Order.objects.select_related("website"),
            pk=order_id,
            website=website,
        )

        requested_deadline = data["requested_deadline"]
        current_deadline = order.writer_deadline

        if current_deadline and requested_deadline <= current_deadline:
            return Response(
                {"detail": "Requested deadline must be later than the current writer deadline."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hours_delta = None
        if current_deadline:
            delta = requested_deadline - current_deadline
            hours_delta = int(delta.total_seconds() / 3600)

        adjustment = OrderAdjustmentRequest.objects.create(
            website=order.website,
            order=order,
            requested_by=user,
            adjustment_type=OrderAdjustmentType.DEADLINE_EXTENSION,
            adjustment_kind="deadline_extension",
            unit_type=OrderScopeUnitType.DEADLINE,
            title=f"Deadline extension request",
            description=data.get("writer_justification", "") or data["reason"],
            writer_justification=data.get("writer_justification", ""),
            client_visible_note=data["reason"],
            current_quantity=0,
            requested_quantity=hours_delta or 0,
            quantity_delta=hours_delta or 0,
            request_total_amount="0.00",
            request_writer_compensation_amount="0.00",
            request_pricing_payload={},
            status=ORDER_ADJUSTMENT_STATUS_PENDING_CLIENT_RESPONSE,
            metadata={
                "deadline_extension": {
                    "requested_deadline": requested_deadline.isoformat(),
                    "current_deadline": current_deadline.isoformat() if current_deadline else None,
                    "hours_requested": hours_delta,
                    "reason": data["reason"],
                }
            },
        )

        try:
            OrderNotificationService.notify_adjustment_created(
                adjustment_request=adjustment,
                created_by=user,
            )
        except Exception:
            pass

        return Response(
            {
                "id": adjustment.pk,
                "status": adjustment.status,
                "adjustment_type": adjustment.adjustment_type,
                "requested_deadline": requested_deadline.isoformat(),
                "hours_requested": hours_delta,
            },
            status=status.HTTP_201_CREATED,
        )
