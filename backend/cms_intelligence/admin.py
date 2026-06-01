"""
Content Intelligence Admin
============================

Operational dashboards for GSC/GA4 data, performance, freshness, attribution.
"""

from django.contrib import admin
from django.utils.html import format_html

from cms_intelligence.models import (
    ContentEmbedding,
    ContentPerformanceSnapshot,
    ConversionAttribution,
    FreshnessAlert,
    GA4DailyMetric,
    GSCDailyMetric,
)


@admin.register(GSCDailyMetric)
class GSCDailyMetricAdmin(admin.ModelAdmin):
    list_display = ["date", "site", "page_path_short", "query_short", "clicks", "impressions", "ctr", "position"]
    list_filter = ["site", "date", "appeared_in_ai_overview"]
    search_fields = ["page_path", "query"]
    date_hierarchy = "date"
    readonly_fields = ["created_at"]

    def page_path_short(self, obj):
        return obj.page_path[:60]

    page_path_short.short_description = "Page"

    def query_short(self, obj):
        return obj.query[:40]

    query_short.short_description = "Query"

    def has_add_permission(self, request):
        return False


@admin.register(GA4DailyMetric)
class GA4DailyMetricAdmin(admin.ModelAdmin):
    list_display = ["date", "site", "page_path_short", "channel", "page_views", "sessions", "conversions"]
    list_filter = ["site", "channel", "date"]
    search_fields = ["page_path"]
    date_hierarchy = "date"

    def page_path_short(self, obj):
        return obj.page_path[:60]

    page_path_short.short_description = "Page"

    def has_add_permission(self, request):
        return False


@admin.register(ContentPerformanceSnapshot)
class ContentPerformanceSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "page_title",
        "site",
        "gsc_clicks_30d",
        "gsc_avg_position_30d",
        "ga4_page_views_30d",
        "internal_conversions_30d",
        "attributed_revenue_30d",
        "diagnosis_badge",
        "last_computed",
    ]
    list_filter = ["site", "diagnosis"]
    search_fields = ["page_title", "page_slug"]
    readonly_fields = [
        "content_type", "object_id", "page_title", "page_slug",
        "gsc_clicks_30d", "gsc_impressions_30d", "gsc_avg_position_30d", "gsc_avg_ctr_30d",
        "ga4_page_views_30d", "ga4_sessions_30d", "ga4_avg_engagement_30d",
        "gsc_clicks_90d", "ga4_page_views_90d",
        "clicks_delta_pct", "position_delta",
        "internal_conversions_30d", "attributed_revenue_30d",
        "ai_overview_appearances_30d", "diagnosis", "last_computed",
    ]

    def diagnosis_badge(self, obj):
        colors = {
            "healthy": "#28a745",
            "low_ctr": "#ffc107",
            "low_engagement": "#fd7e14",
            "no_conversion_path": "#6c757d",
            "declining_position": "#dc3545",
            "not_visible": "#6c757d",
        }
        color = colors.get(obj.diagnosis, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_diagnosis_display(),
        )

    diagnosis_badge.short_description = "Diagnosis"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FreshnessAlert)
class FreshnessAlertAdmin(admin.ModelAdmin):
    list_display = [
        "content_object",
        "alert_type",
        "severity_badge",
        "site",
        "raised_at",
        "resolution",
        "resolved_at",
    ]
    list_filter = ["alert_type", "severity", "resolution", "site"]
    readonly_fields = [
        "content_type", "object_id", "alert_type",
        "severity", "detail", "raised_at",
    ]
    actions = ["acknowledge_alerts", "dismiss_alerts", "mark_updated"]

    def severity_badge(self, obj):
        colors = {1: "#17a2b8", 2: "#28a745", 3: "#ffc107", 4: "#fd7e14", 5: "#dc3545"}
        color = colors.get(obj.severity, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color,
            obj.severity,
        )

    severity_badge.short_description = "Severity"

    @admin.action(description=" Acknowledge selected alerts")
    def acknowledge_alerts(self, request, queryset):
        from django.utils import timezone

        queryset.filter(acknowledged_at__isnull=True).update(
            acknowledged_at=timezone.now(),
            acknowledged_by=request.user,
        )

    @admin.action(description=" Dismiss selected alerts")
    def dismiss_alerts(self, request, queryset):
        from django.utils import timezone

        queryset.filter(resolved_at__isnull=True).update(
            resolved_at=timezone.now(),
            resolution="dismissed",
        )

    @admin.action(description="↻ Mark as content updated")
    def mark_updated(self, request, queryset):
        from django.utils import timezone

        queryset.filter(resolved_at__isnull=True).update(
            resolved_at=timezone.now(),
            resolution="updated",
        )


@admin.register(ConversionAttribution)
class ConversionAttributionAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "content_object",
        "attribution_model",
        "credit_share",
        "attributed_revenue",
        "path_position",
        "path_length",
    ]
    list_filter = ["attribution_model"]
    raw_id_fields = ["order"]
    readonly_fields = [
        "order", "content_type", "object_id",
        "attribution_model", "credit_share", "attributed_revenue",
        "path_position", "path_length", "created_at",
    ]

    def has_add_permission(self, request):
        return False


@admin.register(ContentEmbedding)
class ContentEmbeddingAdmin(admin.ModelAdmin):
    list_display = ["content_object", "model_name", "generated_at"]
    list_filter = ["model_name"]
    readonly_fields = ["content_type", "object_id", "model_name", "source_text_hash", "generated_at"]

    def has_add_permission(self, request):
        return False