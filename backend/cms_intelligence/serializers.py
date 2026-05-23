from rest_framework import serializers

from cms_intelligence.models import (
    ContentPerformanceSnapshot,
    FreshnessAlert,
    GSCDailyMetric,
)


class GSCMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = GSCDailyMetric
        fields = [
            "date", "page_path", "query",
            "clicks", "impressions", "ctr",
            "position", "appeared_in_ai_overview",
        ]


class PerformanceSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentPerformanceSnapshot
        fields = [
            "page_title", "page_slug",
            "gsc_clicks_30d", "gsc_impressions_30d", "gsc_avg_position_30d", "gsc_avg_ctr_30d",
            "ga4_page_views_30d", "ga4_sessions_30d", "ga4_avg_engagement_30d",
            "internal_conversions_30d", "attributed_revenue_30d",
            "gsc_clicks_90d", "ga4_page_views_90d",
            "clicks_delta_pct", "position_delta",
            "ai_overview_appearances_30d", "diagnosis",
            "last_computed",
        ]


class FreshnessAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreshnessAlert
        fields = [
            "id", "alert_type", "severity", "detail",
            "raised_at", "acknowledged_at", "resolved_at", "resolution",
            "content_type", "object_id",
        ]
