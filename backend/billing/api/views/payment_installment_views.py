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