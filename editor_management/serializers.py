from rest_framework import serializers
from .models import (
    EditorProfile,
    EditorTaskAssignment,
    EditorReviewSubmission,
    EditorPerformance,
    EditorNotification,
    EditorActionLog,
)


class EditorProfileSerializer(serializers.ModelSerializer):
    active_tasks_count = serializers.IntegerField(read_only=True)
    can_take_more_tasks = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = EditorProfile
        fields = "__all__"
        read_only_fields = ('user', 'orders_reviewed', 'last_logged_in')


class EditorTaskAssignmentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_topic = serializers.CharField(source='order.topic', read_only=True)
    order_deadline = serializers.DateTimeField(source='order.deadline', read_only=True)
    assigned_editor_name = serializers.CharField(source='assigned_editor.name', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)
    order_status = serializers.CharField(source='order.status', read_only=True)
    
    class Meta:
        model = EditorTaskAssignment
        fields = "__all__"
        read_only_fields = ('assigned_at', 'reviewed_at', 'started_at')


class EditorReviewSubmissionSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_topic = serializers.CharField(source='order.topic', read_only=True)
    editor_name = serializers.CharField(source='editor.name', read_only=True)
    
    class Meta:
        model = EditorReviewSubmission
        fields = "__all__"
        read_only_fields = ('task_assignment', 'editor', 'order', 'submitted_at', 'updated_at')
    
    def validate_quality_score(self, value):
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Quality score must be between 0.00 and 10.00")
        return value


class EditorPerformanceSerializer(serializers.ModelSerializer):
    editor_name = serializers.CharField(source='editor.name', read_only=True)
    
    class Meta:
        model = EditorPerformance
        fields = "__all__"
        read_only_fields = ('editor', 'last_calculated_at')


class EditorNotificationSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='related_order.id', read_only=True, allow_null=True)
    order_topic = serializers.CharField(source='related_order.topic', read_only=True, allow_null=True)
    
    class Meta:
        model = EditorNotification
        fields = "__all__"
        read_only_fields = ('created_at',)


class EditorActionLogSerializer(serializers.ModelSerializer):
    editor_name = serializers.CharField(source='editor.name', read_only=True)
    order_id = serializers.IntegerField(source='related_order.id', read_only=True, allow_null=True)
    
    class Meta:
        model = EditorActionLog
        fields = "__all__"
        read_only_fields = ('timestamp',)


# Serializers for specific actions
class ClaimOrderSerializer(serializers.Serializer):
    """Serializer for claiming an order."""
    order_id = serializers.IntegerField()


class StartReviewSerializer(serializers.Serializer):
    """Serializer for starting a review."""
    task_id = serializers.IntegerField()


class SubmitReviewSerializer(serializers.Serializer):
    """Serializer for submitting a review."""
    task_id = serializers.IntegerField()
    quality_score = serializers.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        required=False,
        allow_null=True
    )
    issues_found = serializers.CharField(required=False, allow_blank=True)
    corrections_made = serializers.CharField(required=False, allow_blank=True)
    recommendations = serializers.CharField(required=False, allow_blank=True)
    is_approved = serializers.BooleanField(default=True)
    requires_revision = serializers.BooleanField(default=False)
    revision_notes = serializers.CharField(required=False, allow_blank=True)
    edited_files = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )


class CompleteTaskSerializer(serializers.Serializer):
    """Serializer for completing a task."""
    task_id = serializers.IntegerField()
    final_notes = serializers.CharField(required=False, allow_blank=True)


class RejectTaskSerializer(serializers.Serializer):
    """Serializer for rejecting a task."""
    task_id = serializers.IntegerField()
    reason = serializers.CharField()


class UnclaimTaskSerializer(serializers.Serializer):
    """Serializer for unclaiming a task."""
    task_id = serializers.IntegerField()


class ManualAssignmentSerializer(serializers.Serializer):
    """Serializer for manual assignment by admin."""
    order_id = serializers.IntegerField()
    editor_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
