from __future__ import annotations

from rest_framework import serializers

from notifications_system.models.digest_notifications import (
    NotificationDigest
)

class NotificationDigestSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationDigest
        fields = [
            'id', 'event_key', 'digest_group', 'category',
            'channels', 'priority',
            'is_sent', 'is_read', 'is_critical',
            'scheduled_for', 'sent_at', 'created_at',
        ]
        read_only_fields = fields