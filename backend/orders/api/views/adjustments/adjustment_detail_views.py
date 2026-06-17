from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order, OrderAdjustmentRequest
from orders.api.serializers.adjustments.adjustment_detail_serializer import (
    AdjustmentDetailSerializer,
)


def _serialize_adjustment(adj: OrderAdjustmentRequest) -> dict:
    proposals = list(
        adj.proposals.order_by("created_at").values(
            "id",
            "proposal_role",
            "proposal_type",
            "unit_type",
            "currency",
            "amount",
            "scope_payload",
            "is_active",
            "created_at",
        )
    )
    data = {
        "id": adj.pk,
        "order_id": adj.order_id,
        "status": adj.status,
        "adjustment_kind": adj.adjustment_kind,
        "adjustment_type": adj.adjustment_type,
        "title": adj.title,
        "description": adj.description,
        "unit_type": adj.unit_type,
        "extra_service_code": adj.extra_service_code,
        "current_quantity": adj.current_quantity,
        "requested_quantity": adj.requested_quantity,
        "countered_quantity": adj.countered_quantity,
        "quantity_delta": adj.quantity_delta,
        "request_total_amount": adj.request_total_amount,
        "counter_total_amount": adj.counter_total_amount,
        "request_writer_compensation_amount": adj.request_writer_compensation_amount,
        "counter_writer_compensation_amount": adj.counter_writer_compensation_amount,
        "requested_by_id": adj.requested_by_id,
        "reviewed_by_id": adj.reviewed_by_id,
        "proposals": proposals,
        "is_counter_final": adj.is_counter_final,
        "escalated_after_counter": adj.escalated_after_counter,
        "expires_at": adj.expires_at,
        "accepted_at": adj.accepted_at,
        "declined_at": adj.declined_at,
        "funded_at": adj.funded_at,
        "applied_at": adj.applied_at,
        "created_at": adj.created_at,
        "updated_at": adj.updated_at,
    }
    return AdjustmentDetailSerializer(data).data


class AdjustmentDetailView(APIView):
    """
    GET /orders/adjustments/{adjustment_id}/
    Read a single adjustment request with its proposals.
    Accessible to: the order client, the assigned writer, and staff.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request: Request,
        adjustment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        user = cast(Any, request.user)
        adj = get_object_or_404(
            OrderAdjustmentRequest.objects.select_related(
                "website", "order"
            ).prefetch_related("proposals"),
            pk=adjustment_id,
            website=user.website,
        )
        return Response(_serialize_adjustment(adj))


class LatestOrderAdjustmentView(APIView):
    """
    GET /orders/{order_id}/adjustments/latest/
    Return the most recent adjustment request for an order, or 404.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        user = cast(Any, request.user)
        order = get_object_or_404(
            Order.objects.select_related("website"),
            pk=order_id,
            website=user.website,
        )
        adj = (
            OrderAdjustmentRequest.objects.filter(order=order)
            .prefetch_related("proposals")
            .order_by("-created_at")
            .first()
        )
        if adj is None:
            return Response(
                {"detail": "No adjustment requests found for this order."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(_serialize_adjustment(adj))
