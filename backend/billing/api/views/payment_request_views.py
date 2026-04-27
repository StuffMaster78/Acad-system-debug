from __future__ import annotations

from decimal import Decimal
from typing import Any, NotRequired, TypedDict, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.permissions.payment_permissions import (
    CanCreateClientPayment,
    CanViewPayments,
)
from billing.api.serializers.payment_request_serializers import (
    PaymentRequestCreateSerializer,
    PaymentRequestIssueSerializer,
    PaymentRequestPreparePaymentSerializer,
    PaymentRequestReadSerializer,
)
from billing.models.payment_request import PaymentRequest
from billing.selectors.payment_request_selectors import (
    PaymentRequestSelector,
)
from billing.services.payment_request_orchestration_service import (
    PaymentRequestOrchestrationService,
)
from billing.services.payment_request_service import PaymentRequestService
from class_management.models import ClassPurchase
from core.utils.request_context import get_request_website
from orders.models.orders import Order
from special_orders.models import SpecialOrder


class PaymentRequestCreateData(TypedDict):
    title: str
    purpose: str
    amount: Decimal
    description: NotRequired[str]
    recipient_email: NotRequired[str]
    recipient_name: NotRequired[str]
    due_at: NotRequired[object | None]
    currency: NotRequired[str]
    order: NotRequired[int | None]
    special_order: NotRequired[int | None]
    class_purchase: NotRequired[int | None]


class PaymentRequestIssueData(TypedDict):
    send_notification: bool


class PaymentRequestPreparePaymentData(TypedDict):
    provider: str
    send_notification: bool


def _reject_tenant_override(*, request: Request) -> None:
    request_data = cast(dict[str, Any], request.data)

    if "website" in request_data or "website_id" in request_data:
        raise PermissionDenied("Tenant cannot be overridden.")


class PaymentRequestListCreateView(APIView):
    """
    List and create billing payment requests for the resolved tenant.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    def get(self, request: Request) -> Response:
        website = get_request_website(request)

        queryset = PaymentRequestSelector.get_queryset_for_website(
            website=website,
        ).order_by("-created_at")

        serializer = PaymentRequestReadSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        website = get_request_website(request)
        _reject_tenant_override(request=request)

        serializer = PaymentRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            PaymentRequestCreateData,
            serializer.validated_data,
        )

        order = None
        order_id = validated.get("order")
        if order_id is not None:
            order = get_object_or_404(
                Order,
                pk=order_id,
                website=website,
            )

        special_order = None
        special_order_id = validated.get("special_order")
        if special_order_id is not None:
            special_order = get_object_or_404(
                SpecialOrder,
                pk=special_order_id,
                website=website,
            )

        class_purchase = None
        class_purchase_id = validated.get("class_purchase")
        if class_purchase_id is not None:
            class_purchase = get_object_or_404(
                ClassPurchase,
                pk=class_purchase_id,
                website=website,
            )

        payment_request = PaymentRequestService.create_payment_request(
            website=website,
            title=validated["title"],
            amount=validated["amount"],
            requested_by=request.user,
            purpose=validated["purpose"],
            description=validated.get("description", ""),
            client=None,
            recipient_email=validated.get("recipient_email", ""),
            recipient_name=validated.get("recipient_name", ""),
            order=order,
            special_order=special_order,
            class_purchase=class_purchase,
            due_at=validated.get("due_at"),
            currency=validated.get("currency", ""),
        )

        output = PaymentRequestReadSerializer(payment_request)
        return Response(output.data, status=status.HTTP_201_CREATED)


class PaymentRequestDetailView(APIView):
    """
    Retrieve a single billing payment request for the resolved tenant.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    @staticmethod
    def _get_payment_request(
        *,
        website: Any,
        payment_request_id: int,
    ) -> PaymentRequest:
        return get_object_or_404(
            PaymentRequest,
            pk=payment_request_id,
            website=website,
        )

    def get(self, request: Request, payment_request_id: int) -> Response:
        website = get_request_website(request)

        payment_request = self._get_payment_request(
            website=website,
            payment_request_id=payment_request_id,
        )

        serializer = PaymentRequestReadSerializer(payment_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentRequestIssueView(APIView):
    """
    Issue a draft billing payment request.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    @staticmethod
    def _get_payment_request(
        *,
        website: Any,
        payment_request_id: int,
    ) -> PaymentRequest:
        return get_object_or_404(
            PaymentRequest,
            pk=payment_request_id,
            website=website,
        )

    def post(self, request: Request, payment_request_id: int) -> Response:
        website = get_request_website(request)
        _reject_tenant_override(request=request)

        serializer = PaymentRequestIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            PaymentRequestIssueData,
            serializer.validated_data,
        )

        payment_request = self._get_payment_request(
            website=website,
            payment_request_id=payment_request_id,
        )

        updated_request = PaymentRequestService.issue_payment_request(
            payment_request=payment_request,
        )

        send_notification = validated["send_notification"]
        if send_notification:
            pass

        output = PaymentRequestReadSerializer(updated_request)
        return Response(output.data, status=status.HTTP_200_OK)


class PaymentRequestPreparePaymentView(APIView):
    """
    Create or reuse a payment intent for a billing payment request.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanCreateClientPayment,
    ]

    @staticmethod
    def _get_payment_request(
        *,
        website: Any,
        payment_request_id: int,
    ) -> PaymentRequest:
        return get_object_or_404(
            PaymentRequest,
            pk=payment_request_id,
            website=website,
        )

    def post(self, request: Request, payment_request_id: int) -> Response:
        website = get_request_website(request)
        _reject_tenant_override(request=request)

        serializer = PaymentRequestPreparePaymentSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        validated = cast(
            PaymentRequestPreparePaymentData,
            serializer.validated_data,
        )

        payment_request = self._get_payment_request(
            website=website,
            payment_request_id=payment_request_id,
        )

        result = (
            PaymentRequestOrchestrationService
            .issue_payment_request_and_prepare_payment(
                payment_request=payment_request,
                provider=validated["provider"],
                send_notification=validated["send_notification"],
                triggered_by=request.user,
            )
        )

        output = {
            "payment_request": PaymentRequestReadSerializer(
                result.payment_request,
            ).data,
            "payment_intent_reference": result.payment_intent.reference,
            "provider_data": result.provider_data,
            "created": result.created,
        }
        return Response(output, status=status.HTTP_200_OK)