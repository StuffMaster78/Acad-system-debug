from __future__ import annotations

from typing import TypedDict

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from websites.models.websites import Website
from writer_management.models.profile import WriterProfile

from writer_payments_management.api.serializers.settlement_action_serializers import (
    RunSettlementSerializer,
)
from writer_payments_management.api.serializers.settlement_serializers import (
    SettlementPeriodSerializer,
)
from writer_payments_management.facade.payments_facade import PaymentsFacade
from writer_payments_management.models.payment_window_models import PaymentWindow
from writer_payments_management.permissions.base import IsFinanceStaff

class RunSettlementData(TypedDict):
    website_id: int
    writer_id: int
    payment_window_id: int
    auto_finalize: bool


class RunSettlementView(APIView):
    permission_classes = [IsFinanceStaff]

    def post(self, request):
        serializer = RunSettlementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data: RunSettlementData = serializer.validated_data  # type: ignore

        website = Website.objects.get(pk=data["website_id"])
        writer = WriterProfile.objects.get(pk=data["writer_id"])
        payment_window = PaymentWindow.objects.get(pk=data["payment_window_id"])

        period = PaymentsFacade.run_settlement(
            website=website,
            writer=writer,
            payment_window=payment_window,
            auto_finalize=data["auto_finalize"],
        )

        response_serializer = SettlementPeriodSerializer(period)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )