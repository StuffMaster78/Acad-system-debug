"""
Serializers for draft request functionality.
"""
from rest_framework import serializers
from orders.models import Order, DraftRequest, DraftFile
from websites.models import Website


class DraftFileSerializer(serializers.ModelSerializer):
    """Serializer for draft files uploaded by writers."""
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    uploaded_by_email = serializers.CharField(source='uploaded_by.email', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = DraftFile
        fields = [
            'id', 'draft_request', 'order', 'uploaded_by', 'uploaded_by_username',
            'uploaded_by_email', 'file', 'file_url', 'file_name', 'file_size',
            'file_size_mb', 'description', 'uploaded_at', 'is_visible_to_client'
        ]
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']
    
    def get_file_url(self, obj):
        """Get the file URL."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_size_mb(self, obj):
        """Get file size in MB."""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class DraftRequestSerializer(serializers.ModelSerializer):
    """Serializer for draft requests."""
    requested_by_username = serializers.CharField(source='requested_by.username', read_only=True)
    requested_by_email = serializers.CharField(source='requested_by.email', read_only=True)
    order_topic = serializers.CharField(source='order.topic', read_only=True)
    order_status = serializers.CharField(source='order.status', read_only=True)
    files = DraftFileSerializer(many=True, read_only=True)
    files_count = serializers.SerializerMethodField()
    can_request = serializers.SerializerMethodField()
    
    class Meta:
        model = DraftRequest
        fields = [
            'id', 'website', 'order', 'order_topic', 'order_status',
            'requested_by', 'requested_by_username', 'requested_by_email',
            'status', 'message', 'requested_at', 'fulfilled_at',
            'cancelled_at', 'files', 'files_count', 'can_request'
        ]
        read_only_fields = ['id', 'requested_at', 'fulfilled_at', 'cancelled_at']
    
    def get_files_count(self, obj):
        """Get count of files uploaded for this request."""
        return obj.files.count()
    
    def get_can_request(self, obj):
        """Check if client can request a draft."""
        can_request, reason = obj.can_request()
        return {
            'can_request': can_request,
            'reason': reason
        }
    
    def validate(self, data):
        """Validate that client can request a draft."""
        order = data.get('order')
        requested_by = data.get('requested_by') or self.context['request'].user
        
        if not order:
            raise serializers.ValidationError("Order is required")
        
        # Check if order belongs to the requesting user
        if order.client != requested_by:
            raise serializers.ValidationError("You can only request drafts for your own orders")
        
        # Check if Progressive Delivery is paid
        draft_request = DraftRequest(
            website=order.website,
            order=order,
            requested_by=requested_by
        )
        can_request, reason = draft_request.can_request()
        if not can_request:
            raise serializers.ValidationError(reason or "Cannot request draft")
        
        # Check if there's already a pending request
        existing_pending = DraftRequest.objects.filter(
            order=order,
            requested_by=requested_by,
            status__in=['pending', 'in_progress']
        ).exists()
        
        if existing_pending:
            raise serializers.ValidationError("You already have a pending draft request for this order")
        
        return data


class DraftRequestCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating draft requests."""
    
    class Meta:
        model = DraftRequest
        fields = ['order', 'message']
    
    def validate_order(self, value):
        """Validate the order."""
        user = self.context['request'].user
        
        # Check if order belongs to user
        if value.client != user:
            raise serializers.ValidationError("You can only request drafts for your own orders")
        
        # Check if Progressive Delivery is paid
        draft_request = DraftRequest(
            website=value.website,
            order=value,
            requested_by=user
        )
        can_request, reason = draft_request.can_request()
        if not can_request:
            raise serializers.ValidationError(reason or "Cannot request draft")
        
        return value

