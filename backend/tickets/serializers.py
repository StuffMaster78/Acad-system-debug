from rest_framework import serializers
from .models import (
    Ticket, TicketMessage, TicketLog, 
    TicketStatistics, TicketAttachment
)   

class TicketMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = TicketMessage
        fields = ['id', 'ticket', 'sender', 'sender_name','website', 'message', 'is_internal', 'created_at']
        read_only_fields = ['id', 'created_at']

class TicketLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True)

    class Meta:
        model = TicketLog
        fields = ['id', 'ticket', 'website', 'action', 'performed_by', 'performed_by_name', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class TicketSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)
    logs = TicketLogSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'created_by', 'created_by_name', 
            'assigned_to', 'assigned_to_name', 'website', 'status', 'priority', 
            'category', 'is_escalated', 'resolution_time', 'created_at', 'updated_at',
            'messages', 'logs'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TicketListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'created_by', 'created_by_name',
            'assigned_to', 'assigned_to_name', 'website', 'status', 'priority',
            'category', 'is_escalated', 'resolution_time', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ['id', 'ticket', 'uploaded_by', 'file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

class TicketCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True,  # Default to read_only, will be made writable in __init__ for support/admin
        required=False,
        allow_null=False,
        help_text="The user this ticket is for (recipient). Required for support/admin creating tickets on behalf of others."
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for created_by field
        from django.contrib.auth import get_user_model
        User = get_user_model()
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            user = request.user
            # Support and admin can create tickets for any user
            if user.role in ['support', 'admin', 'superadmin']:
                self.fields['created_by'].read_only = False
                self.fields['created_by'].queryset = User.objects.all()
            else:
                # Other roles can only create tickets for themselves
                self.fields['created_by'].read_only = True
                self.fields['created_by'].queryset = User.objects.filter(id=user.id)
    
    def validate_created_by(self, value):
        """Validate that created_by is provided for support/admin."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            # Support/admin must specify created_by
            if user.role in ['support', 'admin', 'superadmin']:
                if not value:
                    raise serializers.ValidationError("Please select a user (client, writer, editor, etc.) for this ticket.")
        return value
    
    def create(self, validated_data):
        # website optional: infer from creator if missing
        created_by = validated_data.get('created_by')
        website = validated_data.get('website')
        if website is None and created_by and getattr(created_by, 'website', None):
            validated_data['website'] = created_by.website
        return super().create(validated_data)

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'website', 'priority', 'category', 'created_by']
        extra_kwargs = {
            'website': {'required': False, 'allow_null': True},
        }


class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'website', 'assigned_to', 'is_escalated']

class TicketMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketMessage
        fields = ['ticket', 'sender', 'website', 'message', 'is_internal']
class TicketLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketLog
        fields = ['ticket', 'action', 'website', 'performed_by']

class TicketStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketStatistics
        fields = ['website', 'total_tickets', 'resolved_tickets', 'average_resolution_time', 'created_at']
