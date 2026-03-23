from __future__ import annotations

from rest_framework import serializers

from notifications_system.enums import NotificationChannel
from notifications_system.models.notifications_template import NotificationTemplate
from notifications_system.models.notification_event import (
    NotificationEvent as NotificationEventModel,
)
from notifications_system.models.event_config import NotificationEventConfig
from notifications_system.models.notification_event_override import (
    NotificationEventOverride,
)


class NotificationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationEventModel
        fields = [
            'id', 'event_key', 'label',
            'description', 'category', 'scope', 'is_active',
        ]
        read_only_fields = ['id']


class NotificationTemplateSerializer(serializers.ModelSerializer):
    event_key    = serializers.CharField(source='event.event_key', read_only=True)
    event_label  = serializers.CharField(source='event.label',     read_only=True)
    website_name = serializers.CharField(source='website.name',    read_only=True)
    scope        = serializers.SerializerMethodField()

    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'event', 'event_key', 'event_label',
            'website', 'website_name', 'scope',
            'channel', 'locale', 'version',
            'subject', 'body_html', 'body_text',
            'title', 'message',
            'available_variables', 'provider_overrides',
            'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'event_key', 'event_label',
            'website_name', 'scope', 'created_at', 'updated_at',
        ]

    def get_scope(self, obj) -> str:
        return 'website' if obj.website_id else 'global'


class NotificationTemplateCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = NotificationTemplate
        fields = [
            'event', 'website', 'channel', 'locale', 'version',
            'subject', 'body_html', 'body_text',
            'title', 'message',
            'available_variables', 'provider_overrides', 'is_active',
        ]

    def validate(self, attrs): 
        channel = attrs.get('channel')
        if channel == NotificationChannel.EMAIL:
            if not attrs.get('subject') and not attrs.get('body_html'):
                raise serializers.ValidationError(
                    "Email templates require at least subject or body_html."
                )
        if channel == NotificationChannel.IN_APP:
            if not attrs.get('title') and not attrs.get('message'):
                raise serializers.ValidationError(
                    "In-app templates require at least title or message."
                )
        return attrs       


class NotificationEventConfigSerializer(serializers.ModelSerializer):
    event_key       = serializers.CharField(source='event.event_key', read_only=True)
    default_channels = serializers.SerializerMethodField()

    class Meta:
        model = NotificationEventConfig
        fields = [
            'id', 'event_key', 'label', 'description',
            'supports_email', 'supports_in_app',
            'default_email_enabled', 'default_in_app_enabled',
            'priority', 'recipient_roles',
            'is_mandatory', 'user_can_disable', 'admin_can_disable',
            'digest_eligible', 'digest_group',
            'is_overridable_per_website',
            'cooldown_seconds', 'is_active',
            'default_channels',
        ]
        read_only_fields = ['id', 'event_key', 'default_channels']

    def get_default_channels(self, obj) -> list:
        return obj.get_default_channels()


class NotificationEventOverrideSerializer(serializers.ModelSerializer):
    event_key = serializers.CharField(
        source='event_config.event.event_key', read_only=True
    )

    class Meta:
        model = NotificationEventOverride
        fields = [
            'id', 'website', 'event_config', 'event_key',
            'enabled', 'priority', 'channels', 'roles',
            'template_key', 'fallback_message',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'event_key', 'created_at', 'updated_at']