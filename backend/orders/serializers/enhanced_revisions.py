"""
Enhanced Revision Request Serializers
"""
from rest_framework import serializers
from orders.enhanced_revisions import RevisionRequest


class RevisionRequestSerializer(serializers.ModelSerializer):
    """Serializer for revision requests."""
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_topic = serializers.CharField(source='order.topic', read_only=True)
    requested_by_email = serializers.CharField(source='requested_by.email', read_only=True)
    assigned_to_email = serializers.CharField(source='assigned_to.email', read_only=True)
    timeline = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = RevisionRequest
        fields = [
            'id',
            'website',
            'order',
            'order_id',
            'order_topic',
            'requested_by',
            'requested_by_email',
            'title',
            'description',
            'changes_required',
            'severity',
            'priority',
            'requested_deadline',
            'agreed_deadline',
            'completed_at',
            'status',
            'assigned_to',
            'assigned_to_email',
            'client_notes',
            'writer_notes',
            'is_urgent',
            'requires_client_review',
            'created_at',
            'updated_at',
            'timeline',
            'is_overdue',
            'days_remaining',
        ]
        read_only_fields = [
            'id', 'website', 'order', 'requested_by', 'created_at', 'updated_at',
            'completed_at', 'timeline', 'is_overdue', 'days_remaining'
        ]
    
    def get_timeline(self, obj):
        """Get timeline information."""
        return obj.get_timeline()
    
    def get_is_overdue(self, obj):
        """Check if revision is overdue."""
        timeline = obj.get_timeline()
        return timeline.get('is_overdue', False)
    
    def get_days_remaining(self, obj):
        """Get days remaining until deadline."""
        timeline = obj.get_timeline()
        return timeline.get('days_remaining', None)
    
    def create(self, validated_data):
        """Create revision request."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['requested_by'] = request.user
            validated_data['website'] = request.user.website
        return super().create(validated_data)


class RevisionRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating revision requests."""
    
    class Meta:
        model = RevisionRequest
        fields = [
            'order',
            'title',
            'description',
            'changes_required',
            'severity',
            'priority',
            'requested_deadline',
            'client_notes',
            'is_urgent',
            'requires_client_review',
        ]
    
    def validate_order(self, value):
        """Validate that order belongs to user and can be revised."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("User not found")
        
        # Check order belongs to user
        if value.client != request.user:
            raise serializers.ValidationError("Order does not belong to you")
        
        # Check order status allows revision
        if value.status not in ['completed', 'approved']:
            raise serializers.ValidationError("Order is not in a state that allows revisions")
        
        return value


class RevisionRequestUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating revision requests."""
    
    class Meta:
        model = RevisionRequest
        fields = [
            'title',
            'description',
            'changes_required',
            'severity',
            'priority',
            'requested_deadline',
            'agreed_deadline',
            'client_notes',
            'writer_notes',
            'is_urgent',
            'status',
            'assigned_to',
        ]
        read_only_fields = ['status']  # Status changes through actions


class RevisionRequestCompleteSerializer(serializers.Serializer):
    """Serializer for completing revision requests."""
    writer_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Final notes from writer"
    )
    mark_order_complete = serializers.BooleanField(
        default=False,
        help_text="Whether to mark the order as completed after revision"
    )

