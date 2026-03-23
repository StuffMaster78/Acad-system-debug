from __future__ import annotations

from rest_framework import serializers

from notifications_system.models.delivery import Delivery
from notifications_system.models.notification_log import NotificationLog


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = [
            'id', 'event_key', 'user', 'website',
            'notification', 'channel', 'priority', 'status',
            'attempts', 'max_retries',
            'provider_msg_id', 'error_code', 'error_detail',
            'queued_at', 'sent_at', 'next_retry_at',
            'triggered_by_fallback',
        ]
        read_only_fields = fields


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'user', 'website', 'notification',
            'event_key', 'channel', 'status',
            'is_successful', 'attempt_number',
            'error_code', 'error_detail',
            'provider_msg_id', 'attempted_at',
        ]
        read_only_fields = fields