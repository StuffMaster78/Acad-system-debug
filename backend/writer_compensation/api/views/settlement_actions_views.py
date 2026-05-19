from __future__ import annotations

from typing import cast

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_management.models.writer_profile import WriterProfile

from writer_compensation.api.serializers.settlement_action_serializers import (
    RunSettlementSerializer,
)
from writer_compensation.api.serializers.settlement_serializers import (
    SettlementPeriodSerializer,
)
from writer_compensation.exceptions.exceptions import CompensationError
from writer_compensation.facade.payments_facade import CompensationFacade
from writer_compensation.models.payment_window import PaymentWindow
from writer_compensation.permissions.base import IsFinanceStaff


def _get_website(request):
    return request.website


def _error(message: str, code: int = 400) -> Response:
    return Response({"detail": message}, status=code)


class RunSettlementView(APIView):
    permission_classes = [IsFinanceStaff]

    def post(self, request):
        """
        Run the settlement pipeline for a writer within a payment window.

        POST /settlements/run/

        Body:
        {
            "writer_id": int,
            "payment_window_id": int,
            "auto_finalize": bool
        }
        """
        serializer = RunSettlementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict, serializer.validated_data)

        website = _get_website(request)

        try:
            writer = WriterProfile.objects.get(
                pk=data["writer_id"],
            )

            payment_window = PaymentWindow.objects.get(
                pk=data["payment_window_id"],
                website=website,
            )

        except WriterProfile.DoesNotExist:
            return _error("Writer not found.", status.HTTP_404_NOT_FOUND)

        except PaymentWindow.DoesNotExist:
            return _error(
                "Payment window not found.",
                status.HTTP_404_NOT_FOUND,
            )

        try:
            period = CompensationFacade.run_settlement(
                website=website,
                writer=writer,
                payment_window=payment_window,
                auto_finalize=data.get("auto_finalize", True),
            )

        except (ValueError, CompensationError) as exc:
            return _error(str(exc), status.HTTP_409_CONFLICT)

        response_serializer = SettlementPeriodSerializer(period)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
