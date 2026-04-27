from __future__ import annotations

from typing import Any, NotRequired, TypedDict, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.api.permissions.payment_permissions import CanViewPayments
from billing.api.serializers.reminder_serializers import (
    InvoiceReminderCreateSerializer,
    PaymentRequestReminderCreateSerializer,
    ReminderReadSerializer,
)
from billing.models.invoice import Invoice
from billing.models.payment_request import PaymentRequest
from billing.models.reminder import Reminder
from billing.selectors.reminder_selectors import ReminderSelector
from billing.services.reminder_orchestration_service import (
    ReminderOrchestrationService,
)
from core.utils.request_context import get_request_website


class InvoiceReminderCreateData(TypedDict):
    event_key: NotRequired[str]
    channel: NotRequired[str]
    scheduled_for: NotRequired[object | None]


class PaymentRequestReminderCreateData(TypedDict):
    event_key: NotRequired[str]
    channel: NotRequired[str]
    scheduled_for: NotRequired[object | None]


def _reject_tenant_override(*, request: Request) -> None:
    request_data = cast(dict[str, Any], request.data)

    if "website" in request_data or "website_id" in request_data:
        raise PermissionDenied("Tenant cannot be overridden.")
    

class ReminderListView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    def get(self, request: Request) -> Response:
        website = get_request_website(request)

        queryset = ReminderSelector.get_queryset_for_website(
            website=website,
        ).order_by("-created_at")

        serializer = ReminderReadSerializer(queryset, many=True)
        return Response(serializer.data)
    
class ReminderDetailView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        CanViewPayments,
    ]

    @staticmethod
    def _get_reminder(*, website: Any, reminder_id: int) -> Reminder:
        return get_object_or_404(
            Reminder,
            pk=reminder_id,
            website=website,
        )

    def get(self, request: Request, reminder_id: int) -> Response:
        website = get_request_website(request)

        reminder = self._get_reminder(
            website=website,
            reminder_id=reminder_id,
        )

        serializer = ReminderReadSerializer(reminder)
        return Response(serializer.data)
    

class InvoiceReminderListCreateView(APIView):
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

        queryset = ReminderSelector.get_queryset_for_invoice(
            website=website,
            invoice=invoice,
        ).order_by("-created_at")

        serializer = ReminderReadSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request: Request, invoice_id: int) -> Response:
        website = get_request_website(request)
        _reject_tenant_override(request=request)

        invoice = self._get_invoice(
            website=website,
            invoice_id=invoice_id,
        )

        serializer = InvoiceReminderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(
            InvoiceReminderCreateData,
            serializer.validated_data,
        )

        reminder = ReminderOrchestrationService.schedule_invoice_reminder(
            invoice=invoice,
            event_key=validated.get(
                "event_key",
                "billing.invoice.reminder",
            ),
            channel=validated.get("channel", "email"),
            scheduled_for=validated.get("scheduled_for"),
        )

        return Response(
            ReminderReadSerializer(reminder).data,
            status=status.HTTP_201_CREATED,
        )
    
class PaymentRequestReminderListCreateView(APIView):
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

    def get(
        self,
        request: Request,
        payment_request_id: int,
    ) -> Response:
        website = get_request_website(request)

        payment_request = self._get_payment_request(
            website=website,
            payment_request_id=payment_request_id,
        )

        queryset = ReminderSelector.get_queryset_for_payment_request(
            website=website,
            payment_request=payment_request,
        ).order_by("-created_at")

        serializer = ReminderReadSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(
        self,
        request: Request,
        payment_request_id: int,
    ) -> Response:
        website = get_request_website(request)
        _reject_tenant_override(request=request)

        payment_request = self._get_payment_request(
            website=website,
            payment_request_id=payment_request_id,
        )

        serializer = PaymentRequestReminderCreateSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        validated = cast(
            PaymentRequestReminderCreateData,
            serializer.validated_data,
        )

        reminder = (
            ReminderOrchestrationService
            .schedule_payment_request_reminder(
                payment_request=payment_request,
                event_key=validated.get(
                    "event_key",
                    "billing.payment_request.reminder",
                ),
                channel=validated.get("channel", "email"),
                scheduled_for=validated.get("scheduled_for"),
            )
        )

        return Response(
            ReminderReadSerializer(reminder).data,
            status=status.HTTP_201_CREATED,
        )