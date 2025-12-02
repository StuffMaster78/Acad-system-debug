"""
Analytics Serializers
"""
from rest_framework import serializers
from analytics.models import (
    ClientAnalytics, ClientAnalyticsSnapshot,
    WriterAnalytics, WriterAnalyticsSnapshot,
    ClassAnalytics, ClassPerformanceReport
)


class ClientAnalyticsSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for client analytics snapshots."""
    client_email = serializers.EmailField(source='client.email', read_only=True)
    
    class Meta:
        model = ClientAnalyticsSnapshot
        fields = [
            'id', 'client', 'client_email', 'website', 'snapshot_date',
            'snapshot_type', 'total_spend', 'total_orders',
            'on_time_delivery_rate', 'revision_rate', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ClientAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for client analytics."""
    client_email = serializers.EmailField(source='client.email', read_only=True)
    client_name = serializers.CharField(source='client.username', read_only=True)
    snapshots = ClientAnalyticsSnapshotSerializer(many=True, read_only=True)
    
    class Meta:
        model = ClientAnalytics
        fields = [
            'id', 'client', 'client_email', 'client_name', 'website',
            'period_start', 'period_end',
            'total_spend', 'average_order_value', 'total_orders',
            'on_time_delivery_count', 'late_delivery_count', 'on_time_delivery_rate',
            'total_revisions', 'revision_rate', 'average_revisions_per_order',
            'top_writers', 'average_writer_rating',
            'calculated_at', 'snapshots'
        ]
        read_only_fields = ['id', 'calculated_at']


class WriterAnalyticsSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for writer analytics snapshots."""
    writer_email = serializers.EmailField(source='writer.email', read_only=True)
    
    class Meta:
        model = WriterAnalyticsSnapshot
        fields = [
            'id', 'writer', 'writer_email', 'website', 'snapshot_date',
            'snapshot_type', 'total_earnings', 'effective_hourly_rate',
            'revision_rate', 'approval_rate', 'average_rating', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WriterAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for writer analytics."""
    writer_email = serializers.EmailField(source='writer.email', read_only=True)
    writer_name = serializers.CharField(source='writer.username', read_only=True)
    snapshots = WriterAnalyticsSnapshotSerializer(many=True, read_only=True)
    
    class Meta:
        model = WriterAnalytics
        fields = [
            'id', 'writer', 'writer_email', 'writer_name', 'website',
            'period_start', 'period_end',
            'total_earnings', 'average_order_earnings',
            'total_hours_worked', 'effective_hourly_rate',
            'total_orders_completed', 'total_orders_in_progress',
            'average_completion_time_hours',
            'total_revisions', 'revision_rate', 'average_revisions_per_order',
            'approval_rate', 'rejection_rate',
            'average_rating', 'quality_score',
            'calculated_at', 'snapshots'
        ]
        read_only_fields = ['id', 'calculated_at']


class ClassPerformanceReportSerializer(serializers.ModelSerializer):
    """Serializer for class performance reports."""
    generated_by_name = serializers.CharField(source='generated_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ClassPerformanceReport
        fields = [
            'id', 'class_analytics', 'report_type', 'generated_by',
            'generated_by_name', 'report_data', 'file', 'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']


class ClassAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for class analytics."""
    reports = ClassPerformanceReportSerializer(many=True, read_only=True)
    reports_count = serializers.IntegerField(source='reports.count', read_only=True)
    
    class Meta:
        model = ClassAnalytics
        fields = [
            'id', 'website', 'class_name', 'class_id',
            'period_start', 'period_end',
            'total_students', 'active_students', 'attendance_rate',
            'total_orders', 'completed_orders', 'completion_rate',
            'average_grade', 'on_time_submission_rate',
            'group_performance', 'calculated_at', 'reports', 'reports_count'
        ]
        read_only_fields = ['id', 'calculated_at']


class ClassAnalyticsCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating class analytics."""
    
    class Meta:
        model = ClassAnalytics
        fields = [
            'website', 'class_name', 'class_id',
            'period_start', 'period_end', 'total_students'
        ]


class ClassPerformanceReportCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating class performance reports."""
    
    class Meta:
        model = ClassPerformanceReport
        fields = ['class_analytics', 'report_type', 'report_data']
    
    def create(self, validated_data):
        validated_data['generated_by'] = self.context['request'].user
        return super().create(validated_data)

