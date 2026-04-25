from __future__ import annotations

from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.serializers.adjustments.create_scope_increment_adjustment_serializer import (
    CreateScopeIncrementAdjustmentSerializer,
)
from orders.models import Order
from orders.services.adjustment_negotiation_service import (
    AdjustmentNegotiationService,
)


class CreateScopeIncrementAdjustmentView(GenericAPIView):
    """
    Create page, slide, diagram, or design concept increment request.
    """

    serializer_class = CreateScopeIncrementAdjustmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, order_id: int, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(Any, request.user)
        order = get_object_or_404(Order, pk=order_id, website=user.website)

        data = serializer.validated_data

        pricing_result = {
            "total_price": "0.00",
            "writer_compensation_amount": "0.00",
        }
        source_pricing_snapshot = None

        adjustment = AdjustmentNegotiationService.create_scope_increment_request(
            website=order.website,
            order=order,
            requested_by=user,
            adjustment_type=data["adjustment_type"],
            unit_type=data["unit_type"],
            requested_quantity=data["requested_quantity"],
            title=data["title"],
            description=data.get("description", ""),
            writer_justification=data.get("writer_justification", ""),
            client_visible_note=data.get("client_visible_note", ""),
            pricing_result=pricing_result,
            source_pricing_snapshot=source_pricing_snapshot,
        )

        return Response(
            {
                "id": adjustment.pk,
                "status": adjustment.status,
                "adjustment_kind": adjustment.adjustment_kind,
                "unit_type": adjustment.unit_type,
            },
            status=status.HTTP_201_CREATED,
        )