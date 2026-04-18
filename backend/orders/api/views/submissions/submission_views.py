from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.submission_permissions import (
    CanCompleteOrder,
    CanReopenOrder,
    CanSubmitOrder,
)
from orders.api.serializers.submissions.complete_order_serializer import (
    CompleteOrderSerializer,
)
from orders.api.serializers.submissions.reopen_order_serializer import (
    ReopenOrderSerializer,
)
from orders.api.serializers.submissions.submit_order_serializer import (
    SubmitOrderSerializer,
)
from orders.models import Order
from orders.services.order_submission_service import (
    OrderSubmissionService,
)


class SubmitOrderView(GenericAPIView):
    """
    Allow the current assigned writer to submit the order.
    """

    serializer_class = SubmitOrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanSubmitOrder,
    ]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )
        self.check_object_permissions(request, order)

        updated_order = OrderSubmissionService.submit_order(
            order=order,
            submitted_by=request.user,
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Order submitted successfully.",
                "order_id": updated_order.pk,
                "status": updated_order.status,
                "submitted_at": updated_order.submitted_at,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_order_for_tenant(
        *,
        request: Request,
        order_id: int,
    ) -> Order:
        user = cast(Any, request.user)
        return get_object_or_404(
            Order.objects.select_related(
                "website",
                "client",
                "preferred_writer",
            ),
            pk=order_id,
            website=user.website,
        )


class CompleteOrderView(GenericAPIView):
    """
    Allow client owner or staff to complete a submitted order.
    """

    serializer_class = CompleteOrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanCompleteOrder,
    ]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )
        self.check_object_permissions(request, order)

        updated_order = OrderSubmissionService.complete_order(
            order=order,
            completed_by=request.user,
            triggered_by=request.user,
            internal_reason=validated_data.get("internal_reason", ""),
        )

        return Response(
            {
                "message": "Order completed successfully.",
                "order_id": updated_order.pk,
                "status": updated_order.status,
                "completed_at": updated_order.completed_at,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_order_for_tenant(
        *,
        request: Request,
        order_id: int,
    ) -> Order:
        user = cast(Any, request.user)
        return get_object_or_404(
            Order.objects.select_related(
                "website",
                "client",
                "preferred_writer",
            ),
            pk=order_id,
            website=user.website,
        )


class ReopenOrderView(GenericAPIView):
    """
    Allow staff to reopen a completed order back to in progress.
    """

    serializer_class = ReopenOrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanReopenOrder,
    ]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )
        self.check_object_permissions(request, order)

        updated_order = OrderSubmissionService.reopen_order(
            order=order,
            reopened_by=request.user,
            reason=validated_data["reason"],
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Order reopened successfully.",
                "order_id": updated_order.pk,
                "status": updated_order.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_order_for_tenant(
        *,
        request: Request,
        order_id: int,
    ) -> Order:
        user = cast(Any, request.user)
        return get_object_or_404(
            Order.objects.select_related(
                "website",
                "client",
                "preferred_writer",
            ),
            pk=order_id,
            website=user.website,
        )