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


# ===========================================================================
# AI Answer Engine — public search + admin analytics
# ===========================================================================

class AnswersSearchView(viewsets.ViewSet):
    """
    GET /cms/intelligence/answers/?q=<query>
    Public: full-text search across live blog posts + service pages.
    Returns ranked excerpts suitable for an inline AskWidget.
    POST (public): also accepts { query } body.
    """
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 3:
            return Response({"results": [], "query": query})

        site = getattr(request, "site", None)
        results = []

        try:
            from wagtail.models import Page
            from cms_blog.models import BlogPostPage

            pages = BlogPostPage.objects.live().public()
            if site:
                pages = pages.filter(slug__isnull=False)

            # Wagtail search (uses configured backend — DB search by default)
            hits = pages.search(query)[:6]
            for hit in hits:
                results.append({
                    "title": hit.title,
                    "url": hit.full_url or f"/{hit.slug}",
                    "excerpt": getattr(hit, "excerpt", "") or getattr(hit, "search_description", ""),
                    "type": "blog",
                })
        except Exception:
            pass

        # Log the query (non-fatal)
        try:
            from cms_intelligence.models import SiteSearchLog
            if site:
                SiteSearchLog.objects.create(
                    site=site,
                    query=query,
                    results_count=len(results),
                    top_result_url=results[0]["url"] if results else "",
                    top_result_title=results[0]["title"] if results else "",
                    session_key=request.session.session_key or "" if hasattr(request, "session") else "",
                )
        except Exception:
            pass

        return Response({"results": results, "query": query})


class SearchLogAnalyticsView(viewsets.ViewSet):
    """
    GET /cms/intelligence/search-log/
    Admin: top queries, volume over time, zero-result queries.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        from cms_intelligence.models import SiteSearchLog

        site = getattr(request, "site", None)
        qs = SiteSearchLog.objects.all()
        if site:
            qs = qs.filter(site=site)

        days = int(request.query_params.get("days", 30))
        since = timezone.now() - timedelta(days=days)
        qs = qs.filter(created_at__gte=since)

        top_queries = (
            qs.values("query")
            .annotate(count=Count("id"))
            .order_by("-count")[:20]
        )
        zero_results = (
            qs.filter(results_count=0)
            .values("query")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        return Response({
            "total_searches": qs.count(),
            "period_days": days,
            "top_queries": list(top_queries),
            "zero_result_queries": list(zero_results),
        })


# ===========================================================================
# Personalization Rules CRUD
# ===========================================================================

from rest_framework import serializers as drf_serializers


class PersonalizationRuleSerializer(drf_serializers.ModelSerializer):
    persona_display = drf_serializers.CharField(
        source="get_persona_display", read_only=True
    )

    class Meta:
        from cms_intelligence.models import PersonalizationRule
        model = PersonalizationRule
        fields = [
            "id", "persona", "persona_display",
            "utm_source", "utm_medium", "utm_campaign",
            "hero_headline", "hero_subheadline",
            "cta_label", "cta_url", "trust_badge",
            "is_active", "priority",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "persona_display", "created_at", "updated_at"]


class PersonalizationRuleViewSet(viewsets.ModelViewSet):
    serializer_class = PersonalizationRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from cms_intelligence.models import PersonalizationRule
        site = getattr(self.request, "site", None)
        qs = PersonalizationRule.objects.all()
        if site:
            qs = qs.filter(site=site)
        return qs.order_by("-priority", "persona")

    def perform_create(self, serializer):
        site = getattr(self.request, "site", None)
        serializer.save(site=site)

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def active(self, request):
        """
        GET /cms/intelligence/personalization/active/
        Public: returns all active rules so the frontend can apply them
        without needing auth. No sensitive data exposed.
        """
        from cms_intelligence.models import PersonalizationRule
        site = getattr(request, "site", None)
        qs = PersonalizationRule.objects.filter(is_active=True)
        if site:
            qs = qs.filter(site=site)
        return Response(PersonalizationRuleSerializer(qs.order_by("-priority"), many=True).data)