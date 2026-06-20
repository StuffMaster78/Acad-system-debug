from __future__ import annotations

from typing import cast

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.api.serializers.payment_window_serializers import (
    PaymentWindowChangeRequestCreateSerializer,
    PaymentWindowChangeRequestSerializer,
)
from writer_compensation.api.serializers.writer_payout_serializers import (
    WriterCurrentWindowSerializer,
    WriterEventSerializer,
    WriterPayoutPreferenceSerializer,
    WriterPayoutRecordSerializer,
)
from writer_compensation.enums.compensation_enums import WindowType
from writer_compensation.exceptions.exceptions import (
    CycleChangeNotAllowedError,
)
from writer_compensation.permissions.permissions import IsWriter
from writer_compensation.selectors.payout_selectors import (
    PayoutSelectors,
)
from writer_compensation.selectors.writer_selectors import (
    WriterSelectors,
)
from writer_compensation.services.cycle_change_service import (
    PaymentCycleChangeService,
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


class WriterCurrentWindowView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)

        data = WriterSelectors.get_writer_current_window_status(
            writer,
            website,
        )

        if data["window"] is None:
            return Response(
                {
                    "window": None,
                    "net": "0.00",
                    "count": 0,
                    "is_processing": False,
                }
            )

        serializer = WriterCurrentWindowSerializer(data)

        return Response(serializer.data)


class WriterEventListView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)

        filters = {
            "event_type": request.query_params.get("event_type"),
            "status": request.query_params.get("status"),
            "window_id": request.query_params.get("window_id"),
            "from_date": request.query_params.get("from_date"),
            "to_date": request.query_params.get("to_date"),
            "source_type": request.query_params.get("source_type"),
            "source_id": request.query_params.get("source_id"),
        }

        events = WriterSelectors.get_writer_events(
            writer,
            website,
            filters,
        )

        serializer = WriterEventSerializer(
            events,
            many=True,
        )

        return Response(serializer.data)


class WriterPayoutHistoryView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        writer = _get_writer_profile(request)

        records = PayoutSelectors.get_writer_payout_history(
            writer,
        )

        serializer = WriterPayoutRecordSerializer(
            records,
            many=True,
        )

        return Response(serializer.data)


class WriterLifetimeSummaryView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)

        summary = WriterSelectors.get_writer_lifetime_summary(
            writer,
            website,
        )

        return Response(summary)


class WriterPayoutPreferenceView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)

        preference = (
            WriterSelectors.get_writer_payout_preference(
                writer,
                website,
            )
        )

        if not preference:
            return Response(
                {"detail": "No preference set yet."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WriterPayoutPreferenceSerializer(
            preference,
        )

        return Response(serializer.data)

    def post(self, request):
        from writer_compensation.models.writer_payout_preference import (
            WriterPayoutPreference,
        )

        website = _get_website(request)
        writer = _get_writer_profile(request)

        existing = (
            WriterSelectors.get_writer_payout_preference(
                writer,
                website,
            )
        )

        if existing and existing.locked:
            return _error(
                (
                    "Your payout cycle is locked. "
                    "Submit a cycle change request."
                ),
                status.HTTP_409_CONFLICT,
            )

        cycle_type = request.data.get("cycle_type")

        if cycle_type not in dict(WindowType.choices):
            return _error(
                "Invalid cycle_type.",
                status.HTTP_400_BAD_REQUEST,
            )

        preference, _ = (
            WriterPayoutPreference.objects.update_or_create(
                website=website,
                writer=writer,
                defaults={
                    "cycle_type": cycle_type,
                    "locked": True,
                },
            )
        )

        serializer = WriterPayoutPreferenceSerializer(
            preference,
        )

        return Response(serializer.data)


class WriterCycleChangeRequestView(APIView):
    permission_classes = [IsWriter]

    def get(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)

        pending = (
            WriterSelectors.get_pending_cycle_change_request(
                writer,
                website,
            )
        )

        if not pending:
            return Response(
                {
                    "detail": (
                        "No pending cycle change request."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PaymentWindowChangeRequestSerializer(
            pending,
        )

        return Response(serializer.data)

    def post(self, request):
        website = _get_website(request)
        writer = _get_writer_profile(request)

        serializer = (
            PaymentWindowChangeRequestCreateSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(raise_exception=True)

        validated = cast(
            dict,
            serializer.validated_data,
        )

        try:
            change_request = (
                PaymentCycleChangeService.request_change(
                    website=website,
                    writer=writer,
                    requested_cycle=validated[
                        "requested_cycle"
                    ],
                    reason=validated.get("reason", ""),
                )
            )

        except CycleChangeNotAllowedError as exc:
            return _error(
                str(exc),
                status.HTTP_409_CONFLICT,
            )

        response_serializer = (
            PaymentWindowChangeRequestSerializer(
                change_request,
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class WriterOrderRateCardView(APIView):
    """
    GET /writer/compensation/orders/<order_id>/rate-card/

    Returns the RateCardSnapshot captured at assignment time for the
    given order. Only accessible by the writer who was assigned to it.
    Returns 404 when no snapshot exists (order not yet assigned).
    """

    permission_classes = [IsWriter]

    def get(self, request, order_id: int):
        from django.shortcuts import get_object_or_404
        from writer_compensation.models.rate_card_snapshot import RateCardSnapshot

        writer = _get_writer_profile(request)

        snapshot = get_object_or_404(
            RateCardSnapshot.objects.select_related("order"),
            order_id=order_id,
            writer=writer,
            website=_get_website(request),
        )

        return Response({
            "order_id": order_id,
            "level_name": snapshot.level_name,
            "earning_mode": snapshot.earning_mode,
            "currency": snapshot.currency,
            "rates": {
                "base_pay_per_page": str(snapshot.base_pay_per_page),
                "base_pay_per_slide": str(snapshot.base_pay_per_slide),
                "base_pay_per_chart": str(snapshot.base_pay_per_chart),
                "additional_page_pay": str(snapshot.additional_page_pay),
                "additional_slide_pay": str(snapshot.additional_slide_pay),
                "additional_chart_pay": str(snapshot.additional_chart_pay),
            },
            "urgency": {
                "urgent_time_threshold_hours": snapshot.urgent_time_threshold_hours,
                "urgent_order_surcharge": str(snapshot.urgent_order_surcharge),
                "urgent_multiplier": str(snapshot.urgent_multiplier),
            },
            "tip_percentage": str(snapshot.tip_percentage),
            "snapshotted_at": snapshot.snapshotted_at,
        })