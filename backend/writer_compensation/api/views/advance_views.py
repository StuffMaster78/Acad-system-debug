from __future__ import annotations

from typing import cast

from django.db.models import QuerySet
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from authentication.permissions import IsAdminOrSuperAdmin

from writer_compensation.api.serializers.advance_serializers import (
    AdvancePaymentRequestSerializer,
    ApproveAdvanceSerializer,
    RecordAdvanceRecoverySerializer,
    RequestAdvanceSerializer,
)
from writer_compensation.enums.compensation_enums import (
    AdvancePaymentStatus,
)
from writer_compensation.models.advance_payment import (
    AdvancePaymentRequest,
)
from writer_compensation.models.exposure_ledger import (
    ExposureLedger,
)
from authentication.permissions import IsAdminOrSuperAdmin
from writer_compensation.permissions.permissions import IsWriter
from writer_compensation.selectors.writer_selectors import (
    WriterSelectors,
)
from writer_compensation.services.advance_payment_service import (
    AdvancePaymentService,
)
from writer_compensation.services.risk_engine_service import (
    RiskEngineService,
)


def _get_website(request):
    return request.website


def _get_writer_profile(request):
    from writer_management.utils import get_writer_profile
    return get_writer_profile(request.user)


def _error(
    message: str,
    code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    return Response(
        {"detail": message},
        status=code,
    )


class WriterAdvanceRequestView(APIView):
    """
    GET:
        List the writer's advance requests.

    POST:
        Submit an advance request.
    """

    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)

        advances = (
            AdvancePaymentRequest.objects.filter(
                writer=writer,
                website=website,
            )
            .prefetch_related("recoveries")
            .order_by("-created_at")
        )

        serializer = AdvancePaymentRequestSerializer(
            advances,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)

        serializer = RequestAdvanceSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        validated = cast(
            dict,
            serializer.validated_data,
        )

        try:
            ledger = ExposureLedger.objects.get(
                website=website,
                writer=writer,
            )

        except ExposureLedger.DoesNotExist:
            return _error(
                (
                    "No exposure ledger found. "
                    "Contact support."
                ),
                status.HTTP_404_NOT_FOUND,
            )

        if not AdvancePaymentService.can_request(
            ledger=ledger,
            amount=validated["amount"],
        ):
            cap = RiskEngineService.get_advance_cap(
                ledger=ledger,
            )

            return _error(
                (
                    "Requested amount exceeds available "
                    f"advance capacity of ${cap}."
                ),
                status.HTTP_409_CONFLICT,
            )

        current_window = (
            WriterSelectors.get_writer_current_window_status(
                writer,
                website,
            )
        )

        if not current_window["window"]:
            return _error(
                (
                    "No open payment window. "
                    "Contact support."
                ),
                status.HTTP_409_CONFLICT,
            )

        advance = AdvancePaymentRequest.objects.create(
            website=website,
            writer=writer,
            payment_window=current_window["window"],
            requested_amount=validated["amount"],
            reason=validated["reason"],
            requested_by=request.user,
            status=AdvancePaymentStatus.PENDING,
        )

        response_serializer = (
            AdvancePaymentRequestSerializer(
                advance,
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class AdminAdvanceListView(generics.ListAPIView):
    """
    List advance requests for the current website.
    """

    serializer_class = AdvancePaymentRequestSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    request: Request

    def get_queryset( # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ):
        website = _get_website(self.request)

        status_filter = (
            self.request.query_params.get("status")
        )

        queryset = (
            AdvancePaymentRequest.objects.filter(
                website=website,
            )
            .select_related(
                "writer__account_profile__user",
                "payment_window",
            )
            .prefetch_related("recoveries")
            .order_by("-created_at")
        )

        if status_filter:
            queryset = queryset.filter(
                status=status_filter,
            )

        return cast(
            QuerySet[AdvancePaymentRequest],
            queryset,
        )


class AdminAdvanceApproveView(APIView):
    """
    Approve an advance request.
    """

    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        website = _get_website(request)

        try:
            advance = AdvancePaymentRequest.objects.get(
                pk=pk,
                website=website,
            )

        except AdvancePaymentRequest.DoesNotExist:
            return _error(
                "Advance request not found.",
                status.HTTP_404_NOT_FOUND,
            )

        if (
            advance.status
            != AdvancePaymentStatus.PENDING
        ):
            return _error(
                (
                    "Cannot approve. "
                    f"Status is {advance.status}."
                ),
                status.HTTP_409_CONFLICT,
            )

        serializer = ApproveAdvanceSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        validated = cast(
            dict,
            serializer.validated_data,
        )

        try:
            ledger = ExposureLedger.objects.get(
                website=website,
                writer=advance.writer,
            )

            AdvancePaymentService.apply_advance(
                website=website,
                writer=advance.writer,
                ledger=ledger,
                amount=validated["approved_amount"],
                created_by=request.user,
                advance_request=advance,
            )

        except ValueError as exc:
            return _error(
                str(exc),
                status.HTTP_409_CONFLICT,
            )

        advance.approved_amount = validated[
            "approved_amount"
        ]

        advance.admin_notes = validated.get(
            "admin_notes",
            "",
        )

        advance.status = (
            AdvancePaymentStatus.APPROVED
        )

        advance.reviewed_by = request.user
        advance.reviewed_at = timezone.now()

        advance.save(
            update_fields=[
                "approved_amount",
                "admin_notes",
                "status",
                "reviewed_by",
                "reviewed_at",
            ]
        )

        response_serializer = (
            AdvancePaymentRequestSerializer(
                advance,
            )
        )

        return Response(response_serializer.data)


class AdminAdvanceRejectView(APIView):
    """
    Reject an advance request.
    """

    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        website = _get_website(request)

        try:
            advance = AdvancePaymentRequest.objects.get(
                pk=pk,
                website=website,
            )

        except AdvancePaymentRequest.DoesNotExist:
            return _error(
                "Advance request not found.",
                status.HTTP_404_NOT_FOUND,
            )

        if (
            advance.status
            != AdvancePaymentStatus.PENDING
        ):
            return _error(
                (
                    "Cannot reject. "
                    f"Status is {advance.status}."
                ),
                status.HTTP_409_CONFLICT,
            )

        advance.status = (
            AdvancePaymentStatus.REJECTED
        )

        advance.admin_notes = request.data.get(
            "admin_notes",
            "",
        )

        advance.reviewed_by = request.user
        advance.reviewed_at = timezone.now()

        advance.save(
            update_fields=[
                "status",
                "admin_notes",
                "reviewed_by",
                "reviewed_at",
            ]
        )

        serializer = AdvancePaymentRequestSerializer(
            advance,
        )

        return Response(serializer.data)


class AdminAdvanceRecoveryView(APIView):
    """
    Record an advance repayment installment.
    """

    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, pk):
        website = _get_website(request)

        try:
            advance = AdvancePaymentRequest.objects.get(
                pk=pk,
                website=website,
            )

        except AdvancePaymentRequest.DoesNotExist:
            return _error(
                "Advance request not found.",
                status.HTTP_404_NOT_FOUND,
            )

        if advance.status not in {
            AdvancePaymentStatus.APPROVED,
            AdvancePaymentStatus.PARTIALLY_RECOVERED,
        }:
            return _error(
                (
                    "Cannot record recovery. "
                    f"Status is {advance.status}."
                ),
                status.HTTP_409_CONFLICT,
            )

        serializer = (
            RecordAdvanceRecoverySerializer(
                data=request.data,
            )
        )

        serializer.is_valid(raise_exception=True)

        validated = cast(
            dict,
            serializer.validated_data,
        )

        try:
            ledger = ExposureLedger.objects.get(
                website=website,
                writer=advance.writer,
            )

            AdvancePaymentService.record_recovery(
                website=website,
                writer=advance.writer,
                ledger=ledger,
                advance_request=advance,
                amount=validated["amount"],
                notes=validated.get("notes", ""),
                created_by=request.user,
            )

        except ValueError as exc:
            return _error(
                str(exc),
                status.HTTP_409_CONFLICT,
            )

        advance.refresh_from_db()

        response_serializer = (
            AdvancePaymentRequestSerializer(
                advance,
            )
        )

        return Response(response_serializer.data)