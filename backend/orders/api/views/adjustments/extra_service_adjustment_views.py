from __future__ import annotations

from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.adjustment_permissions import (
    CanActOnOwnAdjustment,
)
from orders.api.serializers.adjustments.client_accept_extra_service_serializer import (
    ClientAcceptExtraServiceSerializer,
)
from orders.api.serializers.adjustments.create_extra_service_adjustment_serializer import (
    CreateExtraServiceAdjustmentSerializer,
)
from orders.models import Order, OrderAdjustmentRequest
from orders.services.adjustment_negotiation_service import (
    AdjustmentNegotiationService,
)


class CreateExtraServiceAdjustmentView(GenericAPIView):
    """
    Create extra service adjustment after order placement.
    """

    serializer_class = CreateExtraServiceAdjustmentSerializer
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
        if data["extra_service_code"] == "progressive delivery":
            pricing_result["progressive_delivery"] = {
                "milestones": data["milestones"],
            }
            
        source_pricing_snapshot = None

        adjustment = AdjustmentNegotiationService.create_extra_service_request(
            website=order.website,
            order=order,
            requested_by=user,
            extra_service_code=data["extra_service_code"],
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
                "extra_service_code": adjustment.extra_service_code,
            },
            status=status.HTTP_201_CREATED,
        )


class ClientAcceptExtraServiceView(GenericAPIView):
    """
    Accept an extra service request.
    """

    serializer_class = ClientAcceptExtraServiceSerializer
    permission_classes = [permissions.IsAuthenticated, CanActOnOwnAdjustment]

    def post(self, request: Request, adjustment_id: int, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        adjustment = get_object_or_404(OrderAdjustmentRequest, pk=adjustment_id)
        self.check_object_permissions(request, adjustment)

        updated = AdjustmentNegotiationService.client_accept_extra_service(
            adjustment_request=adjustment,
            accepted_by=request.user,
        )

        return Response(
            {
                "id": updated.pk,
                "status": updated.status,
            },
            status=status.HTTP_200_OK,
        )