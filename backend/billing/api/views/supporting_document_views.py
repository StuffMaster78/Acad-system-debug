from __future__ import annotations

from typing import Any, NotRequired, TypedDict, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.permissions.payment_permissions import CanViewPayments
from billing.api.serializers.supporting_document_serializers import (
    SupportingDocumentCreateSerializer,
    SupportingDocumentReadSerializer,
)
from billing.models.invoice import Invoice
from billing.models.payment_request import PaymentRequest
from billing.selectors.supporting_document_selectors import (
    SupportingDocumentSelector,
)
from billing.services.supporting_document_service import (
    SupportingDocumentService,
)
from core.utils.request_context import get_request_website


class SupportingDocumentCreateData(TypedDict):
    """
    Typed shape of validated supporting document serializer data.
    """

    file: object
    title: NotRequired[str]
    description: NotRequired[str]

def _reject_tenant_override(*, request: Request) -> None:
    request_data = cast(dict[str, Any], request.data)

    if "website" in request_data or "website_id" in request_data:
        raise PermissionDenied("Tenant cannot be overridden.")

class InvoiceSupportingDocumentListCreateView(APIView):
    """
    List and create supporting documents for an invoice within the
    current tenant.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    @staticmethod
    def _get_invoice(*, website, invoice_id: int) -> Invoice:
        """
        Retrieve a tenant-scoped invoice.

        Args:
            website:
                Tenant website.
            invoice_id:
                Invoice primary key.

        Returns:
            Invoice:
                Matching tenant-scoped invoice.
        """
        return get_object_or_404(
            Invoice,
            pk=invoice_id,
            website=website,
        )

    def get(self, request: Request, invoice_id: int) -> Response:
        """
        List supporting documents linked to an invoice.

        Args:
            request:
                Incoming DRF request.
            invoice_id:
                Invoice primary key.

        Returns:
            Response:
                Serialized supporting document list.
        """

        website = get_request_website(request)

        invoice = self._get_invoice(
            website=website,
            invoice_id=invoice_id,
        )

        queryset = SupportingDocumentSelector.get_queryset_for_invoice(
            website=website,
            invoice=invoice,
        ).order_by("-created_at")
        serializer = SupportingDocumentReadSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, invoice_id: int) -> Response:
        """
        Upload and create a supporting document linked to an invoice.

        Args:
            request:
                Incoming DRF request.
            invoice_id:
                Invoice primary key.

        Returns:
            Response:
                Serialized created supporting document.
        """
        website = get_request_website(request)
        _reject_tenant_override(request=request)

    
        invoice = self._get_invoice(
            website=website,
            invoice_id=invoice_id,
        )

        serializer = SupportingDocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            SupportingDocumentCreateData,
            serializer.validated_data,
        )

        document = SupportingDocumentService.create_document(
            website=website,
            file=validated["file"],
            title=validated.get("title", ""),
            description=validated.get("description", ""),
            invoice=invoice,
        )

        output = SupportingDocumentReadSerializer(document)
        return Response(output.data, status=status.HTTP_201_CREATED)


class PaymentRequestSupportingDocumentListCreateView(APIView):
    """
    List and create supporting documents for a payment request within
    the current tenant.
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
        """
        Retrieve a tenant-scoped payment request.

        Args:
            website:
                Tenant website.
            payment_request_id:
                Payment request primary key.

        Returns:
            PaymentRequest:
                Matching tenant-scoped payment request.
        """
        return get_object_or_404(
            PaymentRequest,
            pk=payment_request_id,
            website=website,
        )

    def get(
        self,
        request: Request,
        payment_request_id: int,
    ) -> Response:
        """
        List supporting documents linked to a payment request.

        Args:
            request:
                Incoming DRF request.
            payment_request_id:
                Payment request primary key.

        Returns:
            Response:
                Serialized supporting document list.
        """
        website = get_request_website(request)

        payment_request = self._get_payment_request(
            website=website,
            payment_request_id=payment_request_id,
        )

        queryset = SupportingDocumentSelector.get_queryset_for_payment_request(
            website=website,
            payment_request=payment_request,
        ).order_by("-created_at")
        serializer = SupportingDocumentReadSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(
        self,
        request: Request,
        payment_request_id: int,
    ) -> Response:
        """
        Upload and create a supporting document linked to a payment
        request.

        Args:
            request:
                Incoming DRF request.
            payment_request_id:
                Payment request primary key.

        Returns:
            Response:
                Serialized created supporting document.
        """
        website = get_request_website(request)

        payment_request = self._get_payment_request(
            website=website,
            payment_request_id=payment_request_id,
        )

        serializer = SupportingDocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            SupportingDocumentCreateData,
            serializer.validated_data,
        )

        document = SupportingDocumentService.create_document(
            website=website,
            file=validated["file"],
            title=validated.get("title", ""),
            description=validated.get("description", ""),
            payment_request=payment_request,
        )

        output = SupportingDocumentReadSerializer(document)
        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
        )