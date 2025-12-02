"""
Serializers for Writer Assignment Acknowledgment
"""
from rest_framework import serializers
from orders.models import WriterAssignmentAcknowledgment


class WriterAssignmentAcknowledgmentSerializer(serializers.ModelSerializer):
    """Serializer for Writer Assignment Acknowledgment"""
    
    writer_username = serializers.CharField(source='writer.username', read_only=True)
    writer_email = serializers.EmailField(source='writer.email', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_title = serializers.CharField(source='order.title', read_only=True)
    
    class Meta:
        model = WriterAssignmentAcknowledgment
        fields = [
            'id',
            'order',
            'order_id',
            'order_title',
            'writer',
            'writer_username',
            'writer_email',
            'acknowledged_at',
            'has_sent_message',
            'has_downloaded_files',
            'last_reminder_sent',
            'reminder_count',
            'notes',
            'is_fully_engaged',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'acknowledged_at',
            'last_reminder_sent',
            'reminder_count',
            'is_fully_engaged',
            'created_at',
            'updated_at',
        ]

