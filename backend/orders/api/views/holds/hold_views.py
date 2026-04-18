from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.hold_permissions import (
    CanCancelHoldRequest,
    CanRequestHold,
    CanReviewHold,
)
from orders.api.serializers.holds.hold_activate_serializer import (
    HoldActivateSerializer,
)
from orders.api.serializers.holds.hold_cancel_serializer import (
    HoldCancelSerializer,
)
from orders.api.serializers.holds.hold_release_serializer import (
    HoldReleaseSerializer,
)
from orders.api.serializers.holds.hold_request_serializer import (
    HoldRequestSerializer,
)
from orders.models import Order, OrderHold
from orders.services.order_hold_service import OrderHoldService


class HoldRequestView(GenericAPIView):
    """
    Create a hold request for an order.
    """

    serializer_class = HoldRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanRequestHold,
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

        hold = OrderHoldService.request_hold(
            order=order,
            requested_by=request.user,
            reason=validated_data["reason"],
            internal_notes=validated_data.get("internal_notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Hold request created.",
                "hold_id": hold.pk,
                "order_id": order.pk,
                "status": hold.status,
            },
            status=status.HTTP_201_CREATED,
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


class HoldActivateView(GenericAPIView):
    """
    Activate a pending hold request.
    """

    serializer_class = HoldActivateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanReviewHold,
    ]

    def post(
        self,
        request: Request,
        hold_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        hold = self._get_hold_for_tenant(
            request=request,
            hold_id=hold_id,
        )
        self.check_object_permissions(request, hold)

        updated_hold = OrderHoldService.activate_hold(
            hold=hold,
            activated_by=request.user,
            remaining_seconds=validated_data["remaining_seconds"],
            internal_notes=validated_data.get("internal_notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Hold activated.",
                "hold_id": updated_hold.pk,
                "order_id": updated_hold.order.pk,
                "status": updated_hold.status,
                "remaining_seconds": updated_hold.remaining_seconds,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_hold_for_tenant(
        *,
        request: Request,
        hold_id: int,
    ) -> OrderHold:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderHold.objects.select_related(
                "website",
                "order",
                "requested_by",
            ),
            pk=hold_id,
            website=user.website,
        )


class HoldReleaseView(GenericAPIView):
    """
    Release an active hold and return order to in progress.
    """

    serializer_class = HoldReleaseSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanReviewHold,
    ]

    def post(
        self,
        request: Request,
        hold_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        hold = self._get_hold_for_tenant(
            request=request,
            hold_id=hold_id,
        )
        self.check_object_permissions(request, hold)

        updated_order = OrderHoldService.release_hold(
            hold=hold,
            released_by=request.user,
            internal_notes=validated_data.get("internal_notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Hold released.",
                "order_id": updated_order.pk,
                "status": updated_order.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_hold_for_tenant(
        *,
        request: Request,
        hold_id: int,
    ) -> OrderHold:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderHold.objects.select_related(
                "website",
                "order",
                "requested_by",
            ),
            pk=hold_id,
            website=user.website,
        )


class HoldCancelView(GenericAPIView):
    """
    Cancel a pending hold request.
    """

    serializer_class = HoldCancelSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanCancelHoldRequest,
    ]

    def post(
        self,
        request: Request,
        hold_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        hold = self._get_hold_for_tenant(
            request=request,
            hold_id=hold_id,
        )
        self.check_object_permissions(request, hold)

        updated_hold = OrderHoldService.cancel_hold_request(
            hold=hold,
            cancelled_by=request.user,
            internal_notes=validated_data.get("internal_notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Hold request cancelled.",
                "hold_id": updated_hold.pk,
                "status": updated_hold.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_hold_for_tenant(
        *,
        request: Request,
        hold_id: int,
    ) -> OrderHold:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderHold.objects.select_related(
                "website",
                "order",
                "requested_by",
            ),
            pk=hold_id,
            website=user.website,
        )