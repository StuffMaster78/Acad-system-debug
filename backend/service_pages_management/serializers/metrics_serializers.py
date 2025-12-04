"""
Serializers for service page website-level content metrics.
"""
from rest_framework import serializers
from ..models.enhanced_models import ServiceWebsiteContentMetrics


class ServiceWebsiteContentMetricsSerializer(serializers.ModelSerializer):
    """
    Expose aggregated metrics for service pages per website.
    """

    class Meta:
        model = ServiceWebsiteContentMetrics
        fields = [
            "id",
            "website",
            "calculated_at",
            "total_pages",
            "published_pages",
            "total_clicks",
            "total_conversions",
            "page_metrics",
        ]
        read_only_fields = ["id", "calculated_at"]


