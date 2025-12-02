"""
Serializers for Review Reminders
"""
from rest_framework import serializers
from orders.models import ReviewReminder


class ReviewReminderSerializer(serializers.ModelSerializer):
    """Serializer for Review Reminders"""
    
    client_username = serializers.CharField(source='client.username', read_only=True)
    client_email = serializers.EmailField(source='client.email', read_only=True)
    writer_username = serializers.CharField(source='writer.username', read_only=True, allow_null=True)
    writer_email = serializers.EmailField(source='writer.email', read_only=True, allow_null=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    order_title = serializers.CharField(source='order.title', read_only=True)
    
    class Meta:
        model = ReviewReminder
        fields = [
            'id',
            'order',
            'order_id',
            'order_title',
            'client',
            'client_username',
            'client_email',
            'writer',
            'writer_username',
            'writer_email',
            'order_completed_at',
            'has_reviewed',
            'has_rated',
            'rating',
            'last_reminder_sent',
            'reminder_count',
            'next_reminder_at',
            'is_completed',
            'completed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'order_completed_at',
            'last_reminder_sent',
            'reminder_count',
            'next_reminder_at',
            'is_completed',
            'completed_at',
            'created_at',
            'updated_at',
        ]

