from __future__ import annotations

from rest_framework import generics

from writer_compensation.api.serializers.compensation_event_serializers import (
    CompensationEventSerializer,
)
from writer_compensation.models.compensation_event import (
    CompensationEvent,
)
from writer_compensation.permissions.base import (
    IsFinanceStaff,
)


class FinancialEventListView(generics.ListAPIView):
    serializer_class = CompensationEventSerializer
    permission_classes = [IsFinanceStaff]

    queryset = (
        CompensationEvent.objects.select_related(
            "website",
            "writer",
            "settlement_period",
        )
        .all()
        .order_by("-created_at")
    )


class FinancialEventDetailView(generics.RetrieveAPIView):
    serializer_class = CompensationEventSerializer
    permission_classes = [IsFinanceStaff]

    queryset = (
        CompensationEvent.objects.select_related(
            "website",
            "writer",
            "settlement_period",
        )
        .all()
    )