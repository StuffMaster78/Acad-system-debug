"""
writer_management/api/views/performance_views.py

FIXES APPLIED
-------------
1. writer.performance_snapshots — reverse accessor unknown to Pylance.
   Replaced with explicit WriterPerformanceSnapshot.objects.filter(writer=writer).

2. writer.performance_metrics — same issue.
   Replaced with explicit WriterPerformanceMetrics.objects.filter(writer=writer).

3. get_serializer_class / get_queryset on WriterMetricsListView missing
   # type: ignore[override] — DRF stubs declare return type Never.

4. Duplicate import of WriterPerformanceSnapshot inside except block removed.
"""

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_management.api.permissions import (
    IsAdminUser,
    IsAdminOrWriterOwner,
)


class MyWriterPerformanceView(APIView):
    """
    GET /api/writer-management/me/performance/

    Returns the authenticated writer's own performance record.
    No registration_id needed — resolved from the session user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from writer_management.api.serializers.performance_serializers import (
            WriterPerformanceSerializer,
        )
        from writer_management.models.writer_performance import WriterPerformance
        from writer_management.models.writer_profile import WriterProfile

        try:
            profile = WriterProfile.objects.get(account_profile__user=request.user)
        except WriterProfile.DoesNotExist:
            return Response({"detail": "Writer profile not found."}, status=404)

        try:
            perf = WriterPerformance.objects.get(writer=profile)
        except WriterPerformance.DoesNotExist:
            # Return zeroed record rather than 404 — the writer exists but
            # no performance rows have been created yet (new writer).
            return Response({
                "total_orders": 0, "completed_orders": 0, "cancelled_orders": 0,
                "disputed_orders": 0, "late_deliveries": 0, "on_time_deliveries": 0,
                "revision_count": 0, "average_rating": None, "total_ratings": 0,
                "total_earnings": "0.00", "total_tips_received": "0.00",
                "total_bonuses": "0.00", "total_fines": "0.00", "updated_at": None,
            })

        return Response(WriterPerformanceSerializer(perf).data)


class WriterPerformanceView(APIView):
    """GET /api/writer-management/writers/<rid>/performance/"""
    permission_classes = [IsAdminOrWriterOwner]

    def get(self, request, registration_id):
        from writer_management.api.serializers.performance_serializers import (
            WriterPerformanceSerializer,
        )
        from writer_management.services.writer_profile_service import (
            WriterProfileService,
        )
        from writer_management.models.writer_performance import WriterPerformance

        try:
            writer = WriterProfileService.get_by_registration_id(
                registration_id
            )
        except Exception:
            return Response({"detail": "Writer not found."}, status=404)

        try:
            perf = WriterPerformance.objects.get(writer=writer)
        except WriterPerformance.DoesNotExist:
            return Response(
                {"detail": "No performance record."}, status=404
            )

        return Response(WriterPerformanceSerializer(perf).data)


class WriterPerformanceSnapshotListView(ListAPIView):
    """GET /api/writer-management/writers/<rid>/performance/snapshots/"""
    permission_classes = [IsAdminUser]

    def get_serializer_class(self): # type: ignore[override]
        from writer_management.api.serializers.performance_serializers import (
            WriterPerformanceSnapshotSerializer,
        )
        return WriterPerformanceSnapshotSerializer

    def get_queryset(self): # type: ignore[override]
        from writer_management.models.writer_performance import WriterPerformanceSnapshot
        from writer_management.services.writer_profile_service import (
            WriterProfileService,
        )

        rid = self.kwargs["registration_id"]

        try:
            writer = WriterProfileService.get_by_registration_id(rid)
        except Exception:
            return WriterPerformanceSnapshot.objects.none()

        # Fix 1: was writer.performance_snapshots — reverse accessor
        # unknown to Pylance. Use explicit queryset instead.
        return WriterPerformanceSnapshot.objects.filter(
            writer=writer
        ).order_by("-period_end")


class WriterMetricsListView(ListAPIView):
    """GET /api/writer-management/writers/<rid>/performance/metrics/"""
    permission_classes = [IsAdminUser]

    def get_serializer_class(self): # type: ignore[override]
        # Fix 3: missing type: ignore[override] on both methods
        from writer_management.api.serializers.performance_serializers import (
            WriterPerformanceMetricsSerializer,
        )
        return WriterPerformanceMetricsSerializer

    def get_queryset(self): # type: ignore[override]
        from writer_management.models.writer_performance import WriterPerformanceMetrics
        from writer_management.services.writer_profile_service import (
            WriterProfileService,
        )

        rid = self.kwargs["registration_id"]

        try:
            writer = WriterProfileService.get_by_registration_id(rid)
        except Exception:
            return WriterPerformanceMetrics.objects.none()

        # Fix 2: was writer.performance_metrics — reverse accessor
        # unknown to Pylance. Use explicit queryset instead.
        return WriterPerformanceMetrics.objects.filter(
            writer=writer
        ).order_by("-week_start")