from __future__ import annotations

from typing import Any, TypedDict, cast

from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.serializers.invoice_serializers import InvoiceReadSerializer
from billing.api.serializers.payment_access_serializers import (
    PublicPreparePaymentSerializer,
)
from billing.api.serializers.payment_request_serializers import (
    PaymentRequestReadSerializer,
)
from billing.services.payment_access_service import PaymentAccessService


class PublicPreparePaymentData(TypedDict):
    provider: str


def _reject_tenant_override(*, request: Request) -> None:
    request_data = cast(dict[str, Any], request.data)

    if "website" in request_data or "website_id" in request_data:
        raise PermissionDenied("Tenant cannot be overridden.")


class PublicInvoicePreparePaymentView(APIView):
    """
    Prepare public token-based payment for an invoice.

    Access is controlled by the secure payment token.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, token: str) -> Response:
        _reject_tenant_override(request=request)

        serializer = PublicPreparePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            PublicPreparePaymentData,
            serializer.validated_data,
        )

        result = PaymentAccessService.prepare_invoice_payment_by_token(
            token=token,
            provider=validated["provider"],
        )

        output = {
            "invoice": InvoiceReadSerializer(result.invoice).data,
            "payment_intent_reference": (
                result.preparation_result.payment_intent.reference
            ),
            "provider_data": result.preparation_result.provider_data,
            "created": result.preparation_result.created,
        }
        return Response(output, status=status.HTTP_200_OK)


class PublicPaymentRequestPreparePaymentView(APIView):
    """
    Prepare public token-based payment for a billing payment request.

    Access is controlled by the secure payment token.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, token: str) -> Response:
        _reject_tenant_override(request=request)

        serializer = PublicPreparePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            PublicPreparePaymentData,
            serializer.validated_data,
        )

        result = (
            PaymentAccessService.prepare_payment_request_payment_by_token(
                token=token,
                provider=validated["provider"],
            )
        )

        output = {
            "payment_request": PaymentRequestReadSerializer(
                result.payment_request
            ).data,
            "payment_intent_reference": (
                result.preparation_result.payment_intent.reference
            ),
            "provider_data": result.preparation_result.provider_data,
            "created": result.preparation_result.created,
        }
        return Response(output, status=status.HTTP_200_OK)