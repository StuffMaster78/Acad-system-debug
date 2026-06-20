from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.request_context import resolve_request_website
from orders.models import Order
from orders.services.adjustment_negotiation_service import AdjustmentNegotiationService
from orders.services.deadline_decrease_pricing_service import DeadlineDecreasePricingService
from orders.services.order_notification_service import OrderNotificationService


class DeadlineDecreaseSerializer(serializers.Serializer):
    new_deadline = serializers.DateTimeField()
    reason = serializers.CharField(max_length=500, default="Rush delivery requested")


class CreateDeadlineDecreaseView(APIView):
    """
    POST /api/v1/orders/orders/<order_id>/adjustments/deadline-decrease/

    Client requests a sooner deadline (rush order).

    The endpoint:
    1. Validates new_deadline is earlier than the current client_deadline
    2. Computes the surcharge using site DeadlineRate bands
    3. Creates an already-accepted OrderAdjustmentRequest so the client
       can proceed directly to funding

    Returns the adjustment ID and computed surcharge so the frontend
    can immediately route the client to the funding UI.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, order_id: int, *args: Any, **kwargs: Any) -> Response:
        serializer = DeadlineDecreaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = cast(Any, request.user)
        website = resolve_request_website(request)

        order = get_object_or_404(
            Order.objects.select_related("website"),
            pk=order_id,
            website=website,
        )

        new_deadline = data["new_deadline"]
        current_deadline = order.client_deadline

        if current_deadline and new_deadline >= current_deadline:
            return Response(
                {"detail": "New deadline must be earlier than the current deadline."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pricing = DeadlineDecreasePricingService.compute_surcharge(
            order=order,
            new_deadline=new_deadline,
        )
        surcharge: Decimal = pricing["client_surcharge"]
        writer_comp_delta: Decimal = pricing["writer_comp_delta"]

        adjustment = AdjustmentNegotiationService.create_deadline_decrease_request(
            order=order,
            requested_by=user,
            new_deadline=new_deadline,
            reason=data["reason"],
            surcharge=surcharge,
            writer_comp_delta=writer_comp_delta,
            new_multiplier=pricing["new_multiplier"],
            pricing_meta={
                "new_hours": pricing["new_hours"],
                "original_hours": pricing["original_hours"],
                "new_multiplier": str(pricing["new_multiplier"]),
                "original_multiplier": str(pricing["original_multiplier"]),
                "total_price": str(order.total_price),
                "writer_comp_delta": str(writer_comp_delta),
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
                "new_deadline": new_deadline.isoformat(),
                "surcharge": str(surcharge),
                "surcharge_breakdown": {
                    "original_multiplier": str(pricing["original_multiplier"]),
                    "new_multiplier": str(pricing["new_multiplier"]),
                    "original_hours": pricing["original_hours"],
                    "new_hours": pricing["new_hours"],
                },
                "message": (
                    "Rush delivery request created. Proceed to payment to confirm."
                    if surcharge > 0
                    else "No surcharge required for this deadline change."
                ),
            },
            status=status.HTTP_201_CREATED,
        )
