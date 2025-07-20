from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timesince import timesince

from notifications_system.models.notifications import Notification
from notifications_system.models.notification_profile import (
    NotificationProfile, NotificationGroupProfile,
    GroupNotificationProfile, 
)
from notifications_system.models.notification_preferences import (
    NotificationPreference, EventNotificationPreference,
    RoleNotificationPreference, UserNotificationPreference,
    NotificationEventPreference, NotificationPreferenceGroup
)
from notifications_system.models.broadcast_notification import (
    BroadcastNotification, BroadcastOverride
)
from notifications_system.models.notification_event import NotificationEvent
from notifications_system.models.notification_group import NotificationGroup

from notifications_system.enums import NotificationType
from notifications_system.utils.priority_mapper import (
    get_priority_from_label, get_label_from_priority
)
from notifications_system.utils.priority_mapper import PRIORITY_LABEL_CHOICES
from notifications_system.event_labels import EVENT_LABELS

class NotificationPriorityMetaSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    priority = NotificationPriorityMetaSerializer()
    event_type = serializers.CharField(source='event.type', read_only=True)
    event_label = serializers.SerializerMethodField()
    priority_label = serializers.SerializerMethodField()

    def get_event_label(self, obj):
        return EVENT_LABELS.get(obj.event, obj.event.replace("_", " ").title())

    class Meta:
        model = Notification
        fields = [
            "id", "website", "type", "title", "message", "link", "category",
            "event", "is_read", "sent_at", "created_at", "actor",
            "payload", "rendered_title", "rendered_message", "rendered_link",
            "is_critical", "is_digest", "digest_group", "priority", "priority_label",
            "time_ago", "event_type", "event_label"
        ]
        read_only_fields = ["id", "created_at", "sent_at", "actor", "time_ago"]
        extra_kwargs = {
            "type": {"required": True},
            "title": {"required": True},
            "message": {"required": True},
            "event": {"required": True},
            "category": {"required": False},
            "is_read": {"required": False},
            "is_critical": {"required": False},
            "is_digest": {"required": False},
            "digest_group": {"required": False},
            "priority": {"required": False}
        }

    def get_actor(self, obj):
        if not obj.actor:
            return None
        return {
            "id": obj.actor.id,
            "username": obj.actor.username,
            "email": obj.actor.email,
        }

    def get_time_ago(self, obj):
        return timesince(obj.created_at) + " ago"
    
    def get_priority_label(self, obj):
        return get_priority_from_label(obj.priority)
    
    def get_label_from_priority(self, priority):
        return get_label_from_priority(priority)

    def validate_type(self, value):
        valid_types = [x[0] for x in NotificationType.CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid notification type: {value}")
        return value
    def validate(self, data):
        priority_label = data.get("priority_label")
        if priority_label:
            data["priority"] = get_priority_from_label(priority_label)
        return data

class NotificationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationProfile
        fields = "__all__"
        
class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "id", "receive_email", "receive_sms", "receive_push",
            "receive_in_app", "mute_all", "digest_only", "muted_events",
            "channel_preferences", "user", "website"
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "receive_email": {"required": False},
            "receive_sms": {"required": False},
            "receive_push": {"required": False},
            "receive_in_app": {"required": False},
            "mute_all": {"required": False},
            "digest_only": {"required": False},
            "muted_events": {"required": False},
            "channel_preferences": {"required": False},
            "user": {"required": False},
            "website": {"required": False}
        }

class NotificationGroupProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationGroupProfile
        fields = "__all__"


class EventNotificationPreferenceSerializer(serializers.ModelSerializer):
    """ Serializer for event-specific notification preferences.
    Allows users to set preferences for specific events on a per-website basis.
    """
    class Meta:
        model = EventNotificationPreference
        fields = [
            "id", "event", "website",
            "email_enabled", "sms_enabled", "push_enabled", "in_app_enabled"
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "event": {"required": True},
            "website": {"required": True},
            "email_enabled": {"required": False},
            "sms_enabled": {"required": False},
            "push_enabled": {"required": False},
            "in_app_enabled": {"required": False}
        }
        def validate_event(self, value):
            if not value:
                raise serializers.ValidationError("Event cannot be empty.")
            return value
        def validate_website(self, value):
            if not value:
                raise serializers.ValidationError("Website cannot be empty.")
            return value
        def validate(self, data):
            if not any([
                data.get("email_enabled"),
                data.get("sms_enabled"),
                data.get("push_enabled"),
                data.get("in_app_enabled")
            ]):
                raise serializers.ValidationError("At least one channel must be enabled.")
            return data
        
class BroadcastNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastNotification
        fields = "__all__"


class NotificationEventPreferenceSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source="event.name", read_only=True)
    event_code = serializers.CharField(source="event.event", read_only=True)

    class Meta:
        model = NotificationEventPreference
        fields = [
            "id",
            "event_name",
            "event_code",
            "receive_email",
            "receive_sms",
            "receive_push",
            "receive_in_app",
        ]

class RoleNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleNotificationPreference
        fields = "__all__"

class GroupNotificationProfileSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = GroupNotificationProfile
        fields = ['id', 'group', 'group_name', 'profile']

class BroadcastOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastOverride
        fields = ['id', 'event_type', 'force_channels', 'title', 'message', 'tenant', 'active']

class NotificationPreferenceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreferenceGroup
        fields = ['id', 'name', 'description', 'website', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'name': {'required': True},
            'website': {'required': True}
        }


class NotificationGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationGroup
        fields = "__all__"