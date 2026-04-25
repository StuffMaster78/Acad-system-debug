from __future__ import annotations

from typing import Any

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.adjustment_permissions import (
    CanActOnOwnAdjustment,
)
from orders.api.serializers.adjustments.client_counter_scope_increment_serializer import (
    ClientCounterScopeIncrementSerializer,
)
from orders.models import OrderAdjustmentRequest
from orders.services.adjustment_negotiation_service import (
    AdjustmentNegotiationService,
)


class ClientCounterScopeIncrementView(GenericAPIView):
    """
    Client counters a scope increment request.
    """

    serializer_class = ClientCounterScopeIncrementSerializer
    permission_classes = [permissions.IsAuthenticated, CanActOnOwnAdjustment]

    def post(self, request: Request, adjustment_id: int, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        adjustment = get_object_or_404(OrderAdjustmentRequest, pk=adjustment_id)
        self.check_object_permissions(request, adjustment)

        data = serializer.validated_data

        pricing_result = {
            "total_price": "0.00",
            "writer_compensation_amount": "0.00",
        }
        counter_pricing_snapshot = None

        updated = AdjustmentNegotiationService.client_counter_scope_increment(
            adjustment_request=adjustment,
            countered_quantity=data["countered_quantity"],
            countered_note=data.get("countered_note", ""),
            pricing_result=pricing_result,
            counter_pricing_snapshot=counter_pricing_snapshot,
            countered_by=request.user,
        )

        return Response(
            {
                "id": updated.pk,
                "status": updated.status,
                "countered_quantity": updated.countered_quantity,
                "counter_total_amount": str(updated.counter_total_amount),
            },
            status=status.HTTP_200_OK,
        )