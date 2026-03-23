from __future__ import annotations

from rest_framework import serializers

from notifications_system.models.broadcast_notification import (
    BroadcastNotification,
    BroadcastAcknowledgement,
    BroadcastOverride,
)


class BroadcastNotificationSerializer(serializers.ModelSerializer):
    is_expired           = serializers.BooleanField(read_only=True)
    acknowledgement_count = serializers.SerializerMethodField()
    has_acknowledged     = serializers.SerializerMethodField()

    class Meta:
        model = BroadcastNotification
        fields = [
            'id', 'title', 'message',
            'event_type', 'website',
            'channels', 'target_roles', 'show_to_all',
            'is_blocking', 'is_optional',
            'require_acknowledgement',
            'pinned', 'dismissible',
            'is_active', 'is_expired',
            'scheduled_for', 'sent_at', 'expires_at',
            'acknowledgement_count', 'has_acknowledged',
            'created_at',
        ]
        read_only_fields = [
            'id', 'is_expired', 'sent_at',
            'acknowledgement_count', 'has_acknowledged', 'created_at',
        ]

    def get_acknowledgement_count(self, obj) -> int:
        return obj.acknowledgements.count()

    def get_has_acknowledged(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.acknowledgements.filter(user=request.user).exists()


class BroadcastAcknowledgementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastAcknowledgement
        fields = ['id', 'broadcast', 'via_channel', 'acknowledged_at']
        read_only_fields = fields


class BroadcastOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastOverride
        fields = [
            'id', 'broadcast', 'user', 'website',
            'force_channels', 'role',
            'override_config', 'is_active',
        ]
        read_only_fields = ['id']