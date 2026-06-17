from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models.orders.order import Order
from orders.models.orders.order_cancellation_request import OrderCancellationRequest
from orders.services.order_cancellation_request_service import (
    OrderCancellationRequestService,
)


class CancellationRequestCreateView(APIView):
    """
    Client requests cancellation of an in-progress order.

    POST /orders/{order_id}/cancellation-request/
    GET  /orders/{order_id}/cancellation-request/   — view current request
    """

    permission_classes = [permissions.IsAuthenticated]

    def _get_order(self, order_id: int, user: Any) -> Order:
        return get_object_or_404(
            Order.objects.select_related("website"),
            pk=order_id,
            website=user.website,
        )

    def get(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        order = self._get_order(order_id, request.user)
        req = get_object_or_404(
            OrderCancellationRequest,
            order=order,
            status=OrderCancellationRequest.STATUS_PENDING,
        )
        return Response(
            {
                "id": req.pk,
                "order_id": req.order_id,
                "status": req.status,
                "reason": req.reason,
                "forfeiture_pct": str(req.forfeiture_pct),
                "forfeiture_amount": str(req.forfeiture_amount),
                "refund_amount": str(req.refund_amount),
                "requested_at": req.requested_at,
            }
        )

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        order = self._get_order(order_id, request.user)
        reason = request.data.get("reason", "").strip()
        if not reason:
            return Response(
                {"detail": "reason is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            req = OrderCancellationRequestService.request_cancellation(
                order=order,
                requested_by=request.user,
                reason=reason,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Cancellation request submitted and pending staff review.",
                "id": req.pk,
                "forfeiture_pct": str(req.forfeiture_pct),
                "forfeiture_amount": str(req.forfeiture_amount),
                "refund_amount": str(req.refund_amount),
            },
            status=status.HTTP_201_CREATED,
        )


class CancellationRequestApproveView(APIView):
    """
    Staff approves a pending cancellation request.

    POST /orders/{order_id}/cancellation-request/{req_id}/approve/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        order_id: int,
        req_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        order = get_object_or_404(
            Order.objects.select_related("website"),
            pk=order_id,
            website=request.user.website,
        )
        req = get_object_or_404(OrderCancellationRequest, pk=req_id, order=order)

        refund_destination = request.data.get("refund_destination", "wallet")
        notes = request.data.get("notes", "")
        forfeiture_override = request.data.get("forfeiture_pct_override")

        from decimal import Decimal, InvalidOperation

        if forfeiture_override is not None:
            try:
                forfeiture_override = Decimal(str(forfeiture_override))
            except InvalidOperation:
                return Response(
                    {"detail": "forfeiture_pct_override must be a number."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            OrderCancellationRequestService.approve_cancellation(
                cancellation_request=req,
                reviewed_by=request.user,
                refund_destination=refund_destination,
                forfeiture_pct_override=forfeiture_override,
                notes=notes,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Cancellation approved and order cancelled."},
            status=status.HTTP_200_OK,
        )


class CancellationRequestRejectView(APIView):
    """
    Staff rejects a pending cancellation request, reverting the order status.

    POST /orders/{order_id}/cancellation-request/{req_id}/reject/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        order_id: int,
        req_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        order = get_object_or_404(
            Order.objects.select_related("website"),
            pk=order_id,
            website=request.user.website,
        )
        req = get_object_or_404(OrderCancellationRequest, pk=req_id, order=order)
        notes = request.data.get("notes", "")

        try:
            OrderCancellationRequestService.reject_cancellation(
                cancellation_request=req,
                reviewed_by=request.user,
                notes=notes,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Cancellation request rejected. Order status reverted."},
            status=status.HTTP_200_OK,
        )
