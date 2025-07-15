from rest_framework import serializers
from django.utils.timesince import timesince
from notifications_system.models import Notification, NotificationPreference
from notifications_system.notification_enums import NotificationType
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

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "id", "receive_email", "receive_sms", "receive_push",
            "receive_in_app", "preferred_language"
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "receive_email": {"required": False},
            "receive_sms": {"required": False},
            "receive_push": {"required": False},
            "receive_in_app": {"required": False},
            "preferred_language": {"required": False}
        }