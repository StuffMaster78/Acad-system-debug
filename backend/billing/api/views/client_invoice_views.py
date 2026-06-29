from __future__ import annotations

from typing import Any, TypedDict, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.serializers.invoice_summary_serializers import (
    InvoiceSummarySerializer,
)
from billing.api.serializers.invoice_serializers import InvoiceReadSerializer
from billing.models.invoice import Invoice
from billing.selectors.invoice_selectors import InvoiceSelector
from billing.services.invoice_orchestration_service import (
    InvoiceOrchestrationService,
)
from core.utils.request_context import get_request_website


class _InvoicePreparePaymentData(TypedDict):
    provider: str

class ClientInvoiceListView(APIView):
    """
    List invoices belonging to the authenticated client within the
    current tenant.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        """
        List client invoices.

        Args:
            request:
                Incoming DRF request.

        Returns:
            Response:
                Serialized client invoice summaries.
        """
        website = get_request_website(request)
        queryset = InvoiceSelector.get_queryset_for_client(
            website=website,
            client=request.user,
        ).order_by("-created_at")

        serializer = InvoiceSummarySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientInvoiceDetailView(APIView):
    """
    Retrieve a single invoice belonging to the authenticated client
    within the current tenant.
    """

    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def _get_invoice(
        *,
        website,
        client,
        invoice_id: int,
    ) -> Invoice:
        """
        Retrieve a client-scoped invoice.

        Args:
            website:
                Tenant website.
            client:
                Authenticated client.
            invoice_id:
                Invoice primary key.

        Returns:
            Invoice:
                Matching client-scoped invoice.
        """
        queryset = InvoiceSelector.get_queryset_for_client(
            website=website,
            client=client,
        )
        return get_object_or_404(
            queryset,
            pk=invoice_id,
        )

    def get(self, request: Request, invoice_id: int) -> Response:
        """
        Retrieve a client invoice summary by id.

        Args:
            request:
                Incoming DRF request.
            invoice_id:
                Invoice primary key.

        Returns:
            Response:
                Serialized invoice summary.
        """
        website = get_request_website(request)
        invoice = self._get_invoice(
            website=website,
            client=request.user,
            invoice_id=invoice_id,
        )
        serializer = InvoiceSummarySerializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientInvoicePreparePaymentView(APIView):
    """
    Prepare a Stripe checkout for a client's own invoice.

    The invoice must already be in issued status. Returns a checkout
    URL the frontend redirects to. Idempotent — reuses any existing
    pending intent for the same invoice.
    """

    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def _get_invoice(*, website: Any, client: Any, invoice_id: int) -> Invoice:
        queryset = InvoiceSelector.get_queryset_for_client(
            website=website,
            client=client,
        )
        return get_object_or_404(queryset, pk=invoice_id)

    def post(self, request: Request, invoice_id: int) -> Response:
        website = get_request_website(request)
        invoice = self._get_invoice(
            website=website,
            client=request.user,
            invoice_id=invoice_id,
        )

        provider = cast(
            _InvoicePreparePaymentData,
            {"provider": request.data.get("provider", "stripe")},
        )["provider"]

        result = InvoiceOrchestrationService.create_payment_intent_for_invoice(
            invoice=invoice,
            provider=provider,
        )

        return Response(
            {
                "invoice": InvoiceReadSerializer(result.invoice).data,
                "payment_intent_reference": result.payment_intent.reference,
                "provider_data": result.provider_data,
                "created": result.created,
            },
            status=status.HTTP_200_OK,
        )