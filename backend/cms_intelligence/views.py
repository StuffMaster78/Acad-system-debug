from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from cms_intelligence.models import (
    ContentPerformanceSnapshot,
    FreshnessAlert,
    GSCDailyMetric,
    TaskSyncLog,
)
from cms_intelligence.serializers import (
    FreshnessAlertSerializer,
    GSCMetricSerializer,
    PerformanceSnapshotSerializer,
)


class PerformanceSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PerformanceSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        site = getattr(self.request, "site", None)
        qs = ContentPerformanceSnapshot.objects.all()
        if site:
            qs = qs.filter(site=site)
        diagnosis = self.request.query_params.get("diagnosis")
        if diagnosis:
            qs = qs.filter(diagnosis=diagnosis)
        return qs.order_by("-gsc_clicks_30d")

    @action(detail=False, methods=["get"])
    def top_performers(self, request):
        qs = self.get_queryset()
        metric = request.query_params.get("metric", "clicks")
        order_map = {
            "clicks": "-gsc_clicks_30d",
            "views": "-ga4_page_views_30d",
            "conversions": "-internal_conversions_30d",
            "revenue": "-attributed_revenue_30d",
        }
        order = order_map.get(metric, "-gsc_clicks_30d")
        return Response(
            PerformanceSnapshotSerializer(qs.order_by(order)[:10], many=True).data
        )

    @action(detail=False, methods=["get"])
    def worst_performers(self, request):
        qs = self.get_queryset().exclude(diagnosis="healthy")
        return Response(
            PerformanceSnapshotSerializer(qs[:20], many=True).data
        )

    @action(detail=False, methods=["get"])
    def diagnostics(self, request):
        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)
        from cms_intelligence.services.performance_diagnostics import PerformanceDiagnosticService
        return Response(PerformanceDiagnosticService.get_summary_for_dashboard(site))


class FreshnessAlertViewSet(viewsets.ModelViewSet):
    serializer_class = FreshnessAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        site = getattr(self.request, "site", None)
        qs = FreshnessAlert.objects.all()
        if site:
            qs = qs.filter(site=site)
        status_filter = self.request.query_params.get("status")
        if status_filter == "unresolved":
            qs = qs.filter(resolved_at__isnull=True)
        elif status_filter == "resolved":
            qs = qs.filter(resolved_at__isnull=False)
        return qs.order_by("-severity", "-raised_at")

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        from django.utils import timezone
        alert = self.get_object()
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.save(update_fields=["acknowledged_at", "acknowledged_by"])
        return Response(FreshnessAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        from django.utils import timezone
        alert = self.get_object()
        alert.resolved_at = timezone.now()
        alert.resolution = request.data.get("resolution", "updated")
        alert.save(update_fields=["resolved_at", "resolution"])
        return Response(FreshnessAlertSerializer(alert).data)


class DashboardView(viewsets.ViewSet):
    """GET /cms-api/intelligence/dashboard/ — unified dashboard data."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        site = getattr(request, "site", None)
        if not site:
            return Response({"error": "No site context"}, status=400)

        data = {}

        # Performance summary
        try:
            from cms_intelligence.services.performance_diagnostics import PerformanceDiagnosticService
            data["diagnostics"] = PerformanceDiagnosticService.get_summary_for_dashboard(site)
        except Exception:
            data["diagnostics"] = {}

        # Funnel summary
        try:
            from cms_intelligence.services.funnel_analytics import FunnelAnalyticsService
            data["funnels"] = FunnelAnalyticsService.get_dashboard_summary(site)
        except Exception:
            data["funnels"] = {}

        # Freshness alerts
        unresolved = FreshnessAlert.objects.filter(site=site, resolved_at__isnull=True)
        data["freshness"] = {
            "total_unresolved": unresolved.count(),
            "critical": unresolved.filter(severity__gte=4).count(),
            "recent": FreshnessAlertSerializer(unresolved[:5], many=True).data,
        }

        # Top performers
        snapshots = ContentPerformanceSnapshot.objects.filter(site=site)
        top_by_clicks = snapshots.order_by("-gsc_clicks_30d").first()
        top_by_revenue = snapshots.order_by("-attributed_revenue_30d").first()

        data["top_performers"] = {
            "most_traffic": {
                "title": top_by_clicks.page_title,
                "clicks": top_by_clicks.gsc_clicks_30d,
            } if top_by_clicks else None,
            "most_revenue": {
                "title": top_by_revenue.page_title,
                "revenue": str(top_by_revenue.attributed_revenue_30d),
            } if top_by_revenue else None,
        }

        return Response(data)


class SyncStatusView(viewsets.ViewSet):
    """
    GET /cms-api/intelligence/sync-status/
    Returns the latest sync log entry for each task type,
    giving staff a live view of when intelligence data was last updated.
    """

    permission_classes = [permissions.IsAuthenticated]

    TASKS = ["gsc", "ga4", "freshness", "snapshot", "attribution", "embeddings"]

    def list(self, request):
        result = {}
        for task in self.TASKS:
            latest = TaskSyncLog.objects.filter(task=task).first()
            if latest:
                result[task] = {
                    "status": latest.status,
                    "rows_processed": latest.rows_processed,
                    "ran_at": latest.ran_at.isoformat(),
                    "error_message": latest.error_message or None,
                    "duration_seconds": latest.duration_seconds,
                }
            else:
                result[task] = None

        # Also surface recent failures (last 7 days)
        from django.utils import timezone
        from datetime import timedelta
        recent_failures = (
            TaskSyncLog.objects
            .filter(status="failed", ran_at__gte=timezone.now() - timedelta(days=7))
            .order_by("-ran_at")[:10]
        )
        result["recent_failures"] = [
            {
                "task": f.task,
                "ran_at": f.ran_at.isoformat(),
                "error_message": f.error_message,
            }
            for f in recent_failures
        ]

        return Response(result)