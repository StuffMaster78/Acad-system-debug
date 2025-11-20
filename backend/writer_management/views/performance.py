"""
Writer Performance Views
"""
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from writer_management.models.performance_snapshot import WriterPerformanceSnapshot
from writer_management.serializers import (
    WriterPerformanceSnapshotSerializer,
    WriterPerformanceSummarySerializer,
)


class WriterPerformanceSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to list or retrieve writer performance snapshots.
    """

    queryset = WriterPerformanceSnapshot.objects.all()
    serializer_class = WriterPerformanceSnapshotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        "writer", "website", "period_start", "period_end", "is_cached"
    ]
    ordering_fields = [
        "generated_at", "average_rating", "total_orders", "completion_rate"
    ]
    ordering = ["-generated_at"]


class WriterPerformanceDashboardView(generics.RetrieveAPIView):
    serializer_class = WriterPerformanceSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return (
            WriterPerformanceSnapshot.objects
            .filter(writer__user=self.request.user)
            .order_by("-generated_at")
            .first()
        )

