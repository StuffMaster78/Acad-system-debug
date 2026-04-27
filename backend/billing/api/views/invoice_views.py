from __future__ import annotations

from typing import Any
from decimal import Decimal
from typing import NotRequired, TypedDict, cast
from rest_framework.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.serializers.invoice_serializers import (
    InvoiceCreateSerializer,
    InvoiceIssueSerializer,
    InvoicePreparePaymentSerializer,
    InvoiceReadSerializer,
)
from billing.api.permissions.payment_permissions import (
    CanViewPayments,
    CanCreateClientPayment,
)
from billing.models.invoice import Invoice
from billing.selectors.invoice_selectors import InvoiceSelector
from billing.services.invoice_orchestration_service import (
    InvoiceOrchestrationService,
)
from billing.services.invoice_service import InvoiceService
from class_management.models import ClassPurchase
from orders.models.orders import Order
from special_orders.models import SpecialOrder
from core.utils.request_context import get_request_website

class InvoiceCreateData(TypedDict):
    """
    Typed shape of validated create-invoice serializer data.
    """

    title: str
    purpose: str
    amount: Decimal
    due_at: object
    description: NotRequired[str]
    recipient_email: NotRequired[str]
    recipient_name: NotRequired[str]
    currency: NotRequired[str]
    order_number: NotRequired[str]
    custom_payment_link: NotRequired[str]
    order: NotRequired[int | None]
    special_order: NotRequired[int | None]
    class_purchase: NotRequired[int | None]


class InvoiceIssueData(TypedDict):
    """
    Typed shape of validated issue-invoice serializer data.
    """

    send_notification: bool


class InvoicePreparePaymentData(TypedDict):
    """
    Typed shape of validated prepare-payment serializer data.
    """

    provider: str
    generate_token: bool
    token_expiry_hours: int
    send_notification: bool


class InvoiceListCreateView(APIView):
    """
    List and create invoices for the current tenant.

    Tenant scope is enforced through request.user.website.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    def get(self, request: Request) -> Response:
        """
        List invoices for the authenticated user's tenant.

        Args:
            request:
                Incoming DRF request.

        Returns:
            Response:
                Serialized invoice list.
        """
        website = get_request_website(request)

        queryset = InvoiceSelector.get_queryset_for_website(
            website=website
        ).order_by("-created_at")

        serializer = InvoiceReadSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """
        Create a new draft invoice.

        Args:
            request:
                Incoming DRF request.

        Returns:
            Response:
                Serialized created invoice.
        """
        website = get_request_website(request)
        serializer = InvoiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            InvoiceCreateData,
            serializer.validated_data,
        )

        # BLOCK tenant override
        request_data = cast(dict[str, Any], request.data)

        if "website_id" in request_data or "website" in request_data:
            raise PermissionDenied("Tenant cannot be overridden.")

        order_id = validated.get("order")
        special_order_id = validated.get("special_order")
        class_purchase_id = validated.get("class_purchase")

        
        order = None
        if order_id is not None:
            order = get_object_or_404(
                Order,
                pk=order_id,
                website=request.user.website,
            )

        special_order = None
        if special_order_id is not None:
            special_order = get_object_or_404(
                SpecialOrder,
                pk=special_order_id,
                website=request.user.website,
            )

        class_purchase = None
        if class_purchase_id is not None:
            class_purchase = get_object_or_404(
                ClassPurchase,
                pk=class_purchase_id,
                website=request.user.website,
            )

        invoice = InvoiceService.create_invoice(
            website=website,
            title=validated["title"],
            amount=validated["amount"],
            due_at=validated["due_at"],
            issued_by=request.user,
            purpose=validated["purpose"],
            description=validated.get("description", ""),
            client=None,
            recipient_email=validated.get("recipient_email", ""),
            recipient_name=validated.get("recipient_name", ""),
            order=order,
            special_order=special_order,
            class_purchase=class_purchase,
            order_number=validated.get("order_number", ""),
            currency=validated.get("currency", ""),
            custom_payment_link=validated.get(
                "custom_payment_link",
                "",
            ),
        )

        output = InvoiceReadSerializer(invoice)
        return Response(output.data, status=status.HTTP_201_CREATED)


class InvoiceDetailView(APIView):
    """
    Retrieve a single invoice for the current tenant.
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
        Retrieve an invoice by id.

        Args:
            request:
                Incoming DRF request.
            invoice_id:
                Invoice primary key.

        Returns:
            Response:
                Serialized invoice.
        """
        website = get_request_website(request)
        invoice = self._get_invoice(
            website=website,
            invoice_id=invoice_id,
        )
        serializer = InvoiceReadSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InvoiceIssueView(APIView):
    """
    Issue a draft invoice.
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

    def post(self, request: Request, invoice_id: int) -> Response:
        """
        Issue a draft invoice.

        Args:
            request:
                Incoming DRF request.
            invoice_id:
                Invoice primary key.

        Returns:
            Response:
                Serialized updated invoice.
        """
        website = get_request_website(request)
        serializer = InvoiceIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            InvoiceIssueData,
            serializer.validated_data,
        )

        invoice = get_object_or_404(
            Invoice,
            website=website,
            invoice_id=invoice_id,
        )

        updated_invoice = InvoiceService.issue_invoice(invoice=invoice)

        send_notification = validated["send_notification"]
        if send_notification:
            pass

        output = InvoiceReadSerializer(updated_invoice)
        return Response(output.data, status=status.HTTP_200_OK)


class InvoicePreparePaymentView(APIView):
    """
    Create or reuse a payment intent for an invoice.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanCreateClientPayment,
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

    def post(self, request: Request, invoice_id: int) -> Response:
        """
        Prepare payment for an invoice.

        Args:
            request:
                Incoming DRF request.
            invoice_id:
                Invoice primary key.

        Returns:
            Response:
                Serialized preparation result including provider data.
        """
        website = get_request_website(request)

        serializer = InvoicePreparePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            InvoicePreparePaymentData,
            serializer.validated_data,
        )

        invoice = get_object_or_404(
            Invoice,
            website=website,
            invoice_id=invoice_id,
        )

        result = (
            InvoiceOrchestrationService
            .issue_invoice_and_prepare_payment(
                invoice=invoice,
                provider=validated["provider"],
                generate_token=validated["generate_token"],
                token_expiry_hours=validated["token_expiry_hours"],
                send_notification=validated["send_notification"],
                triggered_by=request.user,
            )
        )

        output = {
            "invoice": InvoiceReadSerializer(result.invoice).data,
            "payment_intent_reference": result.payment_intent.reference,
            "provider_data": result.provider_data,
            "created": result.created,
        }
        return Response(output, status=status.HTTP_200_OK)