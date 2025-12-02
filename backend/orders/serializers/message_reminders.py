"""
Serializers for Message Reminders
"""
from rest_framework import serializers
from orders.models import MessageReminder


class MessageReminderSerializer(serializers.ModelSerializer):
    """Serializer for Message Reminders"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_title = serializers.CharField(source='order.title', read_only=True)
    message_id = serializers.IntegerField(source='message.id', read_only=True, allow_null=True)
    reminder_type_display = serializers.CharField(source='get_reminder_type_display', read_only=True)
    
    class Meta:
        model = MessageReminder
        fields = [
            'id',
            'order',
            'order_id',
            'order_title',
            'message',
            'message_id',
            'user',
            'user_username',
            'user_email',
            'reminder_type',
            'reminder_type_display',
            'is_read',
            'is_responded',
            'last_reminder_sent',
            'reminder_count',
            'next_reminder_at',
            'is_resolved',
            'resolved_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'last_reminder_sent',
            'reminder_count',
            'next_reminder_at',
            'is_resolved',
            'resolved_at',
            'created_at',
            'updated_at',
        ]

