from __future__ import annotations

from rest_framework import generics

from writer_payments_management.api.serializers.financial_event_serializers import (
    FinancialEventSerializer,
)
from writer_payments_management.models.financial_event_models import (
    FinancialEvent,
)
from writer_payments_management.permissions.base import (
    IsFinanceStaff,
)


class FinancialEventListView(generics.ListAPIView):
    serializer_class = FinancialEventSerializer
    permission_classes = [IsFinanceStaff]

    queryset = (
        FinancialEvent.objects.select_related(
            "website",
            "writer",
            "settlement_period",
        )
        .all()
        .order_by("-created_at")
    )


class FinancialEventDetailView(generics.RetrieveAPIView):
    serializer_class = FinancialEventSerializer
    permission_classes = [IsFinanceStaff]

    queryset = (
        FinancialEvent.objects.select_related(
            "website",
            "writer",
            "settlement_period",
        )
        .all()
    )