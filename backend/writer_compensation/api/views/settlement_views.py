from __future__ import annotations

from rest_framework import generics

from writer_compensation.api.serializers.settlement_serializers import (
    SettlementPeriodSerializer,
)
from writer_compensation.models.settlement_period import (
    SettlementPeriod,
)
from writer_compensation.permissions.base import (
    IsFinanceStaff,
)


class SettlementListView(generics.ListAPIView):
    serializer_class = SettlementPeriodSerializer
    permission_classes = [IsFinanceStaff]

    queryset = (
        SettlementPeriod.objects.select_related(
            "website",
            "writer",
            "payment_window",
        )
        .all()
        .order_by("-created_at")
    )


class SettlementDetailView(generics.RetrieveAPIView):
    serializer_class = SettlementPeriodSerializer
    permission_classes = [IsFinanceStaff]

    queryset = (
        SettlementPeriod.objects.select_related(
            "website",
            "writer",
            "payment_window",
        )
        .all()
    )