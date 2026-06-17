from __future__ import annotations

from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models.orders.order import Order
from orders.models.orders.order_direct_assignment import OrderDirectAssignment
from orders.services.order_assignment_acceptance_service import (
    OrderAssignmentAcceptanceService,
)


class AssignmentAcceptView(APIView):
    """
    Writer accepts or views a pending direct assignment.

    GET  /orders/{order_id}/assignment/   — writer sees their pending gate
    POST /orders/{order_id}/assignment/accept/
    """

    permission_classes = [permissions.IsAuthenticated]

    def _get_gate(self, order_id: int, user: Any) -> OrderDirectAssignment:
        order = get_object_or_404(
            Order.objects.select_related("website"),
            pk=order_id,
            website=user.website,
        )
        return get_object_or_404(
            OrderDirectAssignment,
            order=order,
            writer=user,
            status=OrderDirectAssignment.STATUS_PENDING,
        )

    def get(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        gate = self._get_gate(order_id, request.user)
        return Response(
            {
                "gate_id": gate.pk,
                "order_id": gate.order_id,
                "status": gate.status,
                "assigned_at": gate.assigned_at,
                "assigned_by_id": gate.assigned_by_id,
            }
        )

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        gate = self._get_gate(order_id, request.user)
        reason = request.data.get("reason", "")
        from django.core.exceptions import ValidationError

        try:
            OrderAssignmentAcceptanceService.accept(
                gate=gate,
                writer=request.user,
                reason=reason,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Assignment accepted.", "order_id": gate.order_id},
            status=status.HTTP_200_OK,
        )


class AssignmentRejectView(APIView):
    """
    Writer rejects a pending direct assignment.

    POST /orders/{order_id}/assignment/reject/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        order = get_object_or_404(
            Order.objects.select_related("website"),
            pk=order_id,
            website=request.user.website,
        )
        gate = get_object_or_404(
            OrderDirectAssignment,
            order=order,
            writer=request.user,
            status=OrderDirectAssignment.STATUS_PENDING,
        )
        reason = request.data.get("reason", "")
        from django.core.exceptions import ValidationError

        try:
            OrderAssignmentAcceptanceService.reject(
                gate=gate,
                writer=request.user,
                reason=reason,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Assignment rejected. Order returned to staffing pool.",
                "order_id": gate.order_id,
            },
            status=status.HTTP_200_OK,
        )
