from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.adjustment_funding_permissions import (
    CanCreateAdjustmentFunding,
    CanManageAdjustmentFunding,
)
from orders.api.serializers.adjustments.adjustment_apply_payment_serializer import (  # noqa: E501
    AdjustmentApplyPaymentSerializer,
)
from orders.api.serializers.adjustments.adjustment_attach_payment_intent_serializer import (  # noqa: E501
    AdjustmentAttachPaymentIntentSerializer,
)
from orders.api.serializers.adjustments.adjustment_funding_create_serializer import (  # noqa: E501
    AdjustmentFundingCreateSerializer,
)
from orders.api.serializers.adjustments.adjustment_mark_payment_request_serializer import (  # noqa: E501
    AdjustmentMarkPaymentRequestSerializer,
)
from orders.models import OrderAdjustmentFunding, OrderAdjustmentRequest
from orders.services.adjustment_funding_service import (
    AdjustmentFundingService,
)


class AdjustmentFundingCreateView(GenericAPIView):
    """
    Create the initial funding record for an accepted adjustment.
    """

    serializer_class = AdjustmentFundingCreateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanCreateAdjustmentFunding,
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

        funding = AdjustmentFundingService.create_funding_record(
            adjustment_request=adjustment_request,
            amount_expected=validated_data["amount_expected"],
            payment_request_reference=validated_data.get(
                "payment_request_reference",
                "",
            ),
            invoice_reference=validated_data.get(
                "invoice_reference",
                "",
            ),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Adjustment funding record created.",
                "funding_id": funding.pk,
                "adjustment_request_id": adjustment_request.pk,
                "status": funding.status,
                "amount_expected": funding.amount_expected,
                "amount_paid": funding.amount_paid,
            },
            status=status.HTTP_201_CREATED,
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


class AdjustmentAttachPaymentIntentView(GenericAPIView):
    """
    Attach an external payment intent reference to a funding record.
    """

    serializer_class = AdjustmentAttachPaymentIntentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanManageAdjustmentFunding,
    ]

    def post(
        self,
        request: Request,
        funding_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        funding = self._get_funding_for_tenant(
            request=request,
            funding_id=funding_id,
        )
        self.check_object_permissions(request, funding)

        updated_funding = AdjustmentFundingService.attach_payment_intent(
            funding=funding,
            payment_intent_reference=validated_data[
                "payment_intent_reference"
            ],
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Payment intent attached.",
                "funding_id": updated_funding.pk,
                "status": updated_funding.status,
                "payment_intent_reference": (
                    updated_funding.payment_intent_reference
                ),
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_funding_for_tenant(
        *,
        request: Request,
        funding_id: int,
    ) -> OrderAdjustmentFunding:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderAdjustmentFunding.objects.select_related(
                "website",
                "adjustment_request",
            ),
            pk=funding_id,
            website=user.website,
        )


class AdjustmentMarkPaymentRequestView(GenericAPIView):
    """
    Mark that a billing payment request was created for the funding flow.
    """

    serializer_class = AdjustmentMarkPaymentRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanManageAdjustmentFunding,
    ]

    def post(
        self,
        request: Request,
        funding_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        funding = self._get_funding_for_tenant(
            request=request,
            funding_id=funding_id,
        )
        self.check_object_permissions(request, funding)

        updated_funding = (
            AdjustmentFundingService.mark_payment_request_created(
                funding=funding,
                payment_request_reference=validated_data[
                    "payment_request_reference"
                ],
                triggered_by=request.user,
            )
        )

        return Response(
            {
                "message": "Payment request recorded.",
                "funding_id": updated_funding.pk,
                "status": updated_funding.status,
                "payment_request_reference": (
                    updated_funding.payment_request_reference
                ),
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_funding_for_tenant(
        *,
        request: Request,
        funding_id: int,
    ) -> OrderAdjustmentFunding:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderAdjustmentFunding.objects.select_related(
                "website",
                "adjustment_request",
            ),
            pk=funding_id,
            website=user.website,
        )


class AdjustmentApplyPaymentView(GenericAPIView):
    """
    Apply incoming payment to an adjustment funding record.
    """

    serializer_class = AdjustmentApplyPaymentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanManageAdjustmentFunding,
    ]

    def post(
        self,
        request: Request,
        funding_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        funding = self._get_funding_for_tenant(
            request=request,
            funding_id=funding_id,
        )
        self.check_object_permissions(request, funding)

        updated_funding = AdjustmentFundingService.apply_payment(
            funding=funding,
            amount=validated_data["amount"],
            external_reference=validated_data.get(
                "external_reference",
                "",
            ),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Payment applied to adjustment funding.",
                "funding_id": updated_funding.pk,
                "status": updated_funding.status,
                "amount_expected": updated_funding.amount_expected,
                "amount_paid": updated_funding.amount_paid,
                "funded_at": updated_funding.funded_at,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_funding_for_tenant(
        *,
        request: Request,
        funding_id: int,
    ) -> OrderAdjustmentFunding:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderAdjustmentFunding.objects.select_related(
                "website",
                "adjustment_request",
            ),
            pk=funding_id,
            website=user.website,
        )