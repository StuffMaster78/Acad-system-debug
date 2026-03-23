from __future__ import annotations

from rest_framework import serializers

from notifications_system.models.notification_preferences import (
    NotificationPreference,
    NotificationEventPreference,
    NotificationPreferenceProfile,
    RoleNotificationPreference,
)


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'id',
            'email_enabled', 'in_app_enabled',
            'dnd_enabled', 'dnd_start_hour', 'dnd_end_hour',
            'mute_all', 'mute_until',
            'digest_enabled', 'digest_only', 'digest_frequency',
            'min_priority',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


class NotificationEventPreferenceSerializer(serializers.ModelSerializer):
    event_key      = serializers.CharField(source='event.event_key', read_only=True)
    event_label    = serializers.CharField(source='event.label',     read_only=True)
    event_category = serializers.CharField(source='event.category',  read_only=True)

    class Meta:
        model = NotificationEventPreference
        fields = [
            'id',
            'event_key', 'event_label', 'event_category',
            'email_enabled', 'in_app_enabled',
            'digest_enabled', 'is_enabled',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'event_key', 'event_label',
            'event_category', 'updated_at',
        ]


class NotificationPreferenceProfileSerializer(serializers.ModelSerializer):
    website_name   = serializers.CharField(source='website.name', read_only=True)
    assigned_count = serializers.SerializerMethodField()

    class Meta:
        model = NotificationPreferenceProfile
        fields = [
            'id', 'name', 'description',
            'website', 'website_name',
            'email_enabled', 'in_app_enabled',
            'dnd_enabled', 'dnd_start_hour', 'dnd_end_hour',
            'digest_enabled', 'digest_frequency',
            'is_default', 'is_active',
            'assigned_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'website_name', 'assigned_count',
            'created_at', 'updated_at',
        ]

    def get_assigned_count(self, obj) -> int:
        return NotificationPreference.objects.filter(profile=obj).count()


class RoleNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleNotificationPreference
        fields = [
            'id', 'role', 'website',
            'email_enabled', 'in_app_enabled',
            'digest_enabled', 'min_priority',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']