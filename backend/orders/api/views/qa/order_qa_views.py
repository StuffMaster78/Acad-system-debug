from __future__ import annotations

from typing import Any, cast

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.order_qa_permissions import (
    CanReviewOrderQA,
    CanSubmitOrderForQA,
)
from orders.api.serializers.qa.order_qa_serializers import (
    ApproveOrderForClientDeliverySerializer,
    ReturnOrderToWriterSerializer,
    SubmitOrderForQASerializer,
)
from orders.models import Order
from orders.services.order_qa_review_service import OrderQAReviewService


class SubmitOrderForQAView(GenericAPIView):
    """
    Submit an in-progress order for QA review.
    """

    serializer_class = SubmitOrderForQASerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanSubmitOrderForQA,
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

        user = cast(Any, request.user)
        order = get_object_or_404(
            Order,
            pk=order_id,
            website=user.website,
        )
        self.check_object_permissions(request, order)

        try:
            order = OrderQAReviewService.submit_for_qa(
                order=order,
                submitted_by=user,
                note=serializer.validated_data.get("note", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc

        return Response(
            {
                "message": "Order submitted for QA review.",
                "order_id": order.pk,
                "status": order.status,
            },
            status=status.HTTP_200_OK,
        )


class ApproveOrderForClientDeliveryView(GenericAPIView):
    """
    Approve QA-reviewed work for client delivery.
    """

    serializer_class = ApproveOrderForClientDeliverySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanReviewOrderQA,
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

        user = cast(Any, request.user)
        order = get_object_or_404(
            Order,
            pk=order_id,
            website=user.website,
        )
        self.check_object_permissions(request, order)

        try:
            order = OrderQAReviewService.approve_for_client_delivery(
                order=order,
                reviewed_by=user,
                note=serializer.validated_data.get("note", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc

        return Response(
            {
                "message": "Order approved and submitted to client.",
                "order_id": order.pk,
                "status": order.status,
            },
            status=status.HTTP_200_OK,
        )


class ReturnOrderToWriterView(GenericAPIView):
    """
    Return QA-reviewed work to writer for corrections.
    """

    serializer_class = ReturnOrderToWriterSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanReviewOrderQA,
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

        user = cast(Any, request.user)
        order = get_object_or_404(
            Order,
            pk=order_id,
            website=user.website,
        )
        self.check_object_permissions(request, order)

        try:
            order = OrderQAReviewService.return_to_writer(
                order=order,
                reviewed_by=user,
                reason=serializer.validated_data["reason"],
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages) from exc

        return Response(
            {
                "message": "Order returned to writer.",
                "order_id": order.pk,
                "status": order.status,
            },
            status=status.HTTP_200_OK,
        )