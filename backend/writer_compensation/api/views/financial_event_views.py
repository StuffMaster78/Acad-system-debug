from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import generics

from writer_compensation.api.serializers.compensation_event_serializers import (
    CompensationEventSerializer,
)
from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.permissions.base import IsFinanceStaff


def _get_website(request):
    return request.website

class FinancialEventListView(generics.ListAPIView):
    serializer_class = CompensationEventSerializer
    permission_classes = [IsFinanceStaff]

    
    def get_queryset( # pyright: ignore[reportIncompatibleMethodOverride]
              self
        ):
        return (
            CompensationEvent.objects
            .filter(website=_get_website(self.request))
            .select_related("writer", "payment_window", "settlement_period")
            .order_by("-created_at")
        )

class FinancialEventDetailView(generics.RetrieveAPIView):
    serializer_class = CompensationEventSerializer
    permission_classes = [IsFinanceStaff]

    def get_queryset( # pyright: ignore[reportIncompatibleMethodOverride]
            self
        ):
        return (
            CompensationEvent.objects
            .filter(website=_get_website(self.request))
            .select_related("writer", "payment_window", "settlement_period")
        )