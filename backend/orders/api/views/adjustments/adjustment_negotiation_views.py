from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.adjustment_permissions import (
    CanAcceptAdjustment,
    CanCancelAdjustment,
    CanCounterAdjustment,
    CanCreateAdjustment,
    CanDeclineAdjustment,
    CanOverrideAdjustment,
)
from orders.api.serializers.adjustments.adjustment_accept_serializer import (
    AdjustmentAcceptSerializer,
)
from orders.api.serializers.adjustments.adjustment_cancel_serializer import (
    AdjustmentCancelSerializer,
)
from orders.api.serializers.adjustments.adjustment_counter_serializer import (
    AdjustmentCounterSerializer,
)
from orders.api.serializers.adjustments.adjustment_create_serializer import (
    AdjustmentCreateSerializer,
)
from orders.api.serializers.adjustments.adjustment_decline_serializer import (
    AdjustmentDeclineSerializer,
)
from orders.api.serializers.adjustments.adjustment_staff_override_serializer import (  # noqa: E501
    AdjustmentStaffOverrideSerializer,
)
from orders.models import Order, OrderAdjustmentRequest
from orders.services.adjustment_negotiation_service import (
    AdjustmentNegotiationService,
)


class AdjustmentCreateView(GenericAPIView):
    """
    Create an adjustment request with an initial system quote.
    """

    serializer_class = AdjustmentCreateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanCreateAdjustment,
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

        adjustment_request = (
            AdjustmentNegotiationService.create_request_with_system_quote(
                order=order,
                requested_by=request.user,
                adjustment_type=validated_data["adjustment_type"],
                reason=validated_data["reason"],
                quoted_amount=validated_data["quoted_amount"],
                scope_summary=validated_data["scope_summary"],
                triggered_by=request.user,
            )
        )

        return Response(
            {
                "message": "Adjustment request created.",
                "adjustment_request_id": adjustment_request.pk,
                "order_id": order.pk,
                "status": adjustment_request.status,
                "adjustment_type": adjustment_request.adjustment_type,
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


class AdjustmentCounterView(GenericAPIView):
    """
    Record a client counter proposal on an adjustment request.
    """

    serializer_class = AdjustmentCounterSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanCounterAdjustment,
    ]

    def post(
        self,
        request: Request,
        adjustment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        adjustment_request = self._get_adjustment_for_tenant(
            request=request,
            adjustment_id=adjustment_id,
        )
        self.check_object_permissions(request, adjustment_request)

        proposal = AdjustmentNegotiationService.counter_by_client(
            adjustment_request=adjustment_request,
            client=request.user,
            amount=validated_data["amount"],
            notes=validated_data.get("notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Adjustment counter submitted.",
                "proposal_id": proposal.pk,
                "adjustment_request_id": adjustment_request.pk,
                "status": adjustment_request.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_adjustment_for_tenant(
        *,
        request: Request,
        adjustment_id: int,
    ) -> OrderAdjustmentRequest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderAdjustmentRequest.objects.select_related(
                "website",
                "order",
                "requested_by",
            ),
            pk=adjustment_id,
            website=user.website,
        )


class AdjustmentAcceptView(GenericAPIView):
    """
    Accept an adjustment request and set the final agreement amount.
    """

    serializer_class = AdjustmentAcceptSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanAcceptAdjustment,
    ]

    def post(
        self,
        request: Request,
        adjustment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        adjustment_request = self._get_adjustment_for_tenant(
            request=request,
            adjustment_id=adjustment_id,
        )
        self.check_object_permissions(request, adjustment_request)

        proposal = AdjustmentNegotiationService.accept_request(
            adjustment_request=adjustment_request,
            accepted_by=request.user,
            final_amount=validated_data["final_amount"],
            notes=validated_data.get("notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Adjustment accepted.",
                "proposal_id": proposal.pk,
                "adjustment_request_id": adjustment_request.pk,
                "status": adjustment_request.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_adjustment_for_tenant(
        *,
        request: Request,
        adjustment_id: int,
    ) -> OrderAdjustmentRequest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderAdjustmentRequest.objects.select_related(
                "website",
                "order",
                "requested_by",
            ),
            pk=adjustment_id,
            website=user.website,
        )


class AdjustmentDeclineView(GenericAPIView):
    """
    Decline an open adjustment request.
    """

    serializer_class = AdjustmentDeclineSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanDeclineAdjustment,
    ]

    def post(
        self,
        request: Request,
        adjustment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        adjustment_request = self._get_adjustment_for_tenant(
            request=request,
            adjustment_id=adjustment_id,
        )
        self.check_object_permissions(request, adjustment_request)

        updated_request = AdjustmentNegotiationService.decline_request(
            adjustment_request=adjustment_request,
            declined_by=request.user,
            reason=validated_data["reason"],
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Adjustment declined.",
                "adjustment_request_id": updated_request.pk,
                "status": updated_request.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_adjustment_for_tenant(
        *,
        request: Request,
        adjustment_id: int,
    ) -> OrderAdjustmentRequest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderAdjustmentRequest.objects.select_related(
                "website",
                "order",
                "requested_by",
            ),
            pk=adjustment_id,
            website=user.website,
        )


class AdjustmentCancelView(GenericAPIView):
    """
    Cancel an open adjustment request.
    """

    serializer_class = AdjustmentCancelSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanCancelAdjustment,
    ]

    def post(
        self,
        request: Request,
        adjustment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        adjustment_request = self._get_adjustment_for_tenant(
            request=request,
            adjustment_id=adjustment_id,
        )
        self.check_object_permissions(request, adjustment_request)

        updated_request = AdjustmentNegotiationService.cancel_request(
            adjustment_request=adjustment_request,
            cancelled_by=request.user,
            reason=validated_data["reason"],
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Adjustment cancelled.",
                "adjustment_request_id": updated_request.pk,
                "status": updated_request.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_adjustment_for_tenant(
        *,
        request: Request,
        adjustment_id: int,
    ) -> OrderAdjustmentRequest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderAdjustmentRequest.objects.select_related(
                "website",
                "order",
                "requested_by",
            ),
            pk=adjustment_id,
            website=user.website,
        )


class AdjustmentStaffOverrideView(GenericAPIView):
    """
    Create a staff override proposal on an open adjustment request.
    """

    serializer_class = AdjustmentStaffOverrideSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanOverrideAdjustment,
    ]

    def post(
        self,
        request: Request,
        adjustment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        adjustment_request = self._get_adjustment_for_tenant(
            request=request,
            adjustment_id=adjustment_id,
        )
        self.check_object_permissions(request, adjustment_request)

        proposal = (
            AdjustmentNegotiationService.create_staff_override_proposal(
                adjustment_request=adjustment_request,
                proposed_by=request.user,
                amount=validated_data["amount"],
                notes=validated_data["notes"],
                triggered_by=request.user,
            )
        )

        return Response(
            {
                "message": "Staff override proposal created.",
                "proposal_id": proposal.pk,
                "adjustment_request_id": adjustment_request.pk,
                "status": adjustment_request.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_adjustment_for_tenant(
        *,
        request: Request,
        adjustment_id: int,
    ) -> OrderAdjustmentRequest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderAdjustmentRequest.objects.select_related(
                "website",
                "order",
                "requested_by",
            ),
            pk=adjustment_id,
            website=user.website,
        )