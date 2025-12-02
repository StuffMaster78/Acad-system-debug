"""
Serializers for Enhanced Disputes
"""
from rest_framework import serializers
from support_management.models.enhanced_disputes import OrderDispute, DisputeMessage
from django.contrib.auth import get_user_model

User = get_user_model()


class DisputeMessageSerializer(serializers.ModelSerializer):
    """Serializer for dispute messages."""
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    
    class Meta:
        model = DisputeMessage
        fields = [
            'id', 'dispute', 'sender', 'sender_name', 'sender_email',
            'message', 'is_internal', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DisputeMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating dispute messages."""
    
    class Meta:
        model = DisputeMessage
        fields = ['dispute', 'message', 'is_internal']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class OrderDisputeSerializer(serializers.ModelSerializer):
    """Serializer for order disputes."""
    raised_by_name = serializers.CharField(source='raised_by.username', read_only=True)
    raised_by_email = serializers.EmailField(source='raised_by.email', read_only=True)
    other_party_name = serializers.CharField(source='other_party.username', read_only=True)
    other_party_email = serializers.EmailField(source='other_party.email', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True, allow_null=True)
    escalated_to_name = serializers.CharField(source='escalated_to.username', read_only=True, allow_null=True)
    order_title = serializers.CharField(source='order.title', read_only=True)
    order_status = serializers.CharField(source='order.status', read_only=True)
    messages = DisputeMessageSerializer(many=True, read_only=True)
    messages_count = serializers.IntegerField(source='messages.count', read_only=True)
    
    class Meta:
        model = OrderDispute
        fields = [
            'id', 'website', 'order', 'order_title', 'order_status',
            'title', 'description', 'raised_by', 'raised_by_name', 'raised_by_email',
            'other_party', 'other_party_name', 'other_party_email',
            'status', 'priority', 'assigned_to', 'assigned_to_name',
            'resolution_notes', 'resolved_by', 'resolved_by_name',
            'resolved_at', 'resolution_outcome',
            'escalated_at', 'escalated_to', 'escalated_to_name', 'escalation_reason',
            'created_at', 'updated_at', 'messages', 'messages_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'resolved_at', 'escalated_at']


class OrderDisputeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating order disputes."""
    
    class Meta:
        model = OrderDispute
        fields = [
            'order', 'title', 'description', 'other_party', 'priority'
        ]
    
    def validate(self, data):
        """Validate dispute creation."""
        order = data.get('order')
        user = self.context['request'].user
        
        # Ensure user is either client or writer of the order
        if order.client != user and order.writer != user:
            raise serializers.ValidationError(
                "You can only raise disputes for orders you are involved in."
            )
        
        # Set raised_by and other_party
        if order.client == user:
            data['raised_by'] = user
            data['other_party'] = order.writer
        else:
            data['raised_by'] = user
            data['other_party'] = order.client
        
        # Set website from order
        data['website'] = order.website
        
        return data
    
    def create(self, validated_data):
        return super().create(validated_data)


class OrderDisputeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order disputes."""
    
    class Meta:
        model = OrderDispute
        fields = [
            'status', 'priority', 'assigned_to', 'resolution_notes',
            'resolution_outcome', 'escalation_reason'
        ]


class OrderDisputeEscalateSerializer(serializers.Serializer):
    """Serializer for escalating disputes."""
    escalated_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role__in=['admin', 'superadmin'])
    )
    escalation_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_escalated_to(self, value):
        """Validate escalated_to user."""
        if value.role not in ['admin', 'superadmin']:
            raise serializers.ValidationError(
                "Can only escalate to admin or superadmin users."
            )
        return value


class OrderDisputeResolveSerializer(serializers.Serializer):
    """Serializer for resolving disputes."""
    resolution_notes = serializers.CharField()
    resolution_outcome = serializers.ChoiceField(
        choices=['client_wins', 'writer_wins', 'partial_refund', 'extend_deadline', 'reassign']
    )

