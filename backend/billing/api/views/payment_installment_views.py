from __future__ import annotations

from typing import Any, TypedDict, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.permissions.payment_permissions import CanViewPayments
from billing.api.serializers.payment_installment_serializers import (
    PaymentInstallmentCancelSerializer,
    PaymentInstallmentReadSerializer,
    PaymentInstallmentScheduleCreateSerializer,
)
from billing.models.installment import PaymentInstallment
from billing.models.invoice import Invoice
from billing.selectors.payment_installment_selectors import (
    PaymentInstallmentSelector,
)
from billing.services.payment_installment_service import (
    PaymentInstallmentScheduleItem,
    PaymentInstallmentService,
)
from core.utils.request_context import get_request_website


class PaymentInstallmentScheduleData(TypedDict):
    schedule: list[PaymentInstallmentScheduleItem]


def _reject_tenant_override(*, request: Request) -> None:
    request_data = cast(dict[str, Any], request.data)

    if "website" in request_data or "website_id" in request_data:
        raise PermissionDenied("Tenant cannot be overridden.")


class InvoiceInstallmentListCreateView(APIView):
    """
    List and create installment schedules for a tenant-scoped invoice.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    @staticmethod
    def _get_invoice(*, website: Any, invoice_id: int) -> Invoice:
        return get_object_or_404(
            Invoice,
            pk=invoice_id,
            website=website,
        )

    def get(self, request: Request, invoice_id: int) -> Response:
        website = get_request_website(request)

        invoice = self._get_invoice(
            website=website,
            invoice_id=invoice_id,
        )

        queryset = PaymentInstallmentSelector.get_queryset_for_invoice(
            website=website,
            invoice=invoice,
        ).order_by("sequence_number", "due_at")

        serializer = PaymentInstallmentReadSerializer(
            queryset,
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request, invoice_id: int) -> Response:
        website = get_request_website(request)
        _reject_tenant_override(request=request)

        invoice = self._get_invoice(
            website=website,
            invoice_id=invoice_id,
        )

        serializer = PaymentInstallmentScheduleCreateSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        validated = cast(
            PaymentInstallmentScheduleData,
            serializer.validated_data,
        )

        installments = PaymentInstallmentService.create_schedule(
            invoice=invoice,
            schedule=validated["schedule"],
        )

        output = PaymentInstallmentReadSerializer(
            installments,
            many=True,
        )
        return Response(output.data, status=status.HTTP_201_CREATED)


class PaymentInstallmentDetailView(APIView):
    """
    Retrieve a single installment for the resolved tenant.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    @staticmethod
    def _get_installment(
        *,
        website: Any,
        installment_id: int,
    ) -> PaymentInstallment:
        return get_object_or_404(
            PaymentInstallment,
            pk=installment_id,
            website=website,
        )

    def get(self, request: Request, installment_id: int) -> Response:
        website = get_request_website(request)

        installment = self._get_installment(
            website=website,
            installment_id=installment_id,
        )

        serializer = PaymentInstallmentReadSerializer(installment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentInstallmentCancelView(APIView):
    """
    Cancel a tenant-scoped installment.
    """

    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    @staticmethod
    def _get_installment(
        *,
        website: Any,
        installment_id: int,
    ) -> PaymentInstallment:
        return get_object_or_404(
            PaymentInstallment,
            pk=installment_id,
            website=website,
        )

    def post(self, request: Request, installment_id: int) -> Response:
        website = get_request_website(request)
        _reject_tenant_override(request=request)

        installment = self._get_installment(
            website=website,
            installment_id=installment_id,
        )

        serializer = PaymentInstallmentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_installment = PaymentInstallmentService.cancel_installment(
            installment=installment,
        )

        output = PaymentInstallmentReadSerializer(updated_installment)
        return Response(output.data, status=status.HTTP_200_OK)


class InstallmentPreparePaymentView(APIView):
    """
    POST /billing/installments/<id>/prepare-payment/

    Create a payment intent sized to this installment's remaining balance.
    The client uses the returned payment_intent_reference to complete payment
    via Stripe or wallet. When verified, the amount is automatically allocated
    to this installment (and any subsequent ones if it covers them).

    Body: { "provider": "stripe" | "wallet" }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, installment_id: int) -> Response:
        from django.core.exceptions import ValidationError as DjangoValidationError
        from billing.services.invoice_orchestration_service import (
            InvoiceOrchestrationService,
        )

        website = get_request_website(request)
        provider = (request.data.get("provider") or "").strip()
        if not provider:
            return Response(
                {"detail": "provider is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        installment = get_object_or_404(
            PaymentInstallment.objects.select_related(
                "invoice__client",
                "invoice__website",
            ),
            pk=installment_id,
            website=website,
        )

        # Clients may only pay their own invoices
        invoice = installment.invoice
        if (
            hasattr(invoice, "client_id")
            and invoice.client_id is not None
            and invoice.client_id != request.user.pk
            and not getattr(request.user, "is_staff", False)
        ):
            return Response(
                {"detail": "You do not have permission to pay this installment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            result = InvoiceOrchestrationService.create_payment_intent_for_installment(
                installment=installment,
                provider=provider,
                triggered_by=request.user,
            )
        except DjangoValidationError as exc:
            return Response(
                {"detail": exc.message if hasattr(exc, "message") else str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        remaining = installment.amount - installment.amount_paid
        return Response(
            {
                "payment_intent_reference": result.payment_intent.reference,
                "provider_data": result.provider_data,
                "installment_id": installment.pk,
                "installment_sequence": installment.sequence_number,
                "amount": str(remaining),
                "currency": invoice.currency,
                "invoice_reference": invoice.reference,
            },
            status=status.HTTP_200_OK,
        )