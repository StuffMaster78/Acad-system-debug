from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.serializers.invoice_summary_serializers import (
    InvoiceSummarySerializer,
)
from billing.models.invoice import Invoice
from billing.selectors.invoice_selectors import InvoiceSelector
from core.utils.request_context import get_request_website

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