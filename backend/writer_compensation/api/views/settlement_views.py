from __future__ import annotations

from rest_framework import generics

from writer_compensation.api.serializers.settlement_serializers import (
    SettlementPeriodSerializer,
)
from writer_compensation.models.settlement_period import SettlementPeriod
from writer_compensation.permissions.base import IsFinanceStaff


def _get_website(request):
    return request.website


class SettlementListView(generics.ListAPIView):
    serializer_class   = SettlementPeriodSerializer
    permission_classes = [IsFinanceStaff]

    def get_queryset( # pyright: ignore[reportIncompatibleMethodOverride]
            self
    ):
        return (
            SettlementPeriod.objects
            .filter(website=_get_website(self.request))
            .select_related("writer", "payment_window")
            .order_by("-created_at")
        )


class SettlementDetailView(generics.RetrieveAPIView):
    serializer_class   = SettlementPeriodSerializer
    permission_classes = [IsFinanceStaff]

    def get_queryset( # pyright: ignore[reportIncompatibleMethodOverride]
            self
        ):
        return (
            SettlementPeriod.objects
            .filter(website=_get_website(self.request))
            .select_related("writer", "payment_window")
        )