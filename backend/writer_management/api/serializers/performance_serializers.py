from rest_framework import serializers
from writer_management.models.writer_performance import (
    WriterPerformance,
    WriterPerformanceSnapshot,
    WriterPerformanceMetrics,
)
 
 
class WriterPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterPerformance
        fields = [
            "total_orders",
            "completed_orders",
            "cancelled_orders",
            "disputed_orders",
            "late_deliveries",
            "on_time_deliveries",
            "revision_count",
            "average_rating",
            "total_ratings",
            "total_earnings",
            "total_tips_received",
            "total_bonuses",
            "total_fines",
            "updated_at",
        ]
        read_only_fields = fields
 
 
class WriterPerformanceSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterPerformanceSnapshot
        fields = [
            "id",
            "period_start",
            "period_end",
            "total_orders",
            "completed_orders",
            "cancelled_orders",
            "late_orders",
            "revised_orders",
            "disputed_orders",
            "completion_rate",
            "lateness_rate",
            "revision_rate",
            "dispute_rate",
            "cancellation_rate",
            "average_rating",
            "amount_paid",
            "composite_score",
            "better_than_percent",
            "is_processed",
            "generated_at",
        ]
        read_only_fields = fields
 
 
class WriterPerformanceMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterPerformanceMetrics
        fields = [
            "id",
            "week_start",
            "week_end",
            "avg_rating",
            "revision_rate",
            "dispute_rate",
            "lateness_rate",
            "cancellation_rate",
            "total_orders_completed",
            "total_pages_completed",
            "total_earnings",
            "composite_score",
            "percentile_rank",
            "updated_at",
        ]
        read_only_fields = fields