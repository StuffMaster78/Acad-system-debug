# notifications_system/serializers.py
from __future__ import annotations
from typing import Any, Dict, Optional

from django.utils import timezone
from django.utils.timesince import timesince
from rest_framework import serializers

from notifications_system.enums import NotificationType
from notifications_system.event_labels import EVENT_LABELS

from notifications_system.models.notifications import Notification
from notifications_system.models.notification_profile import (
    NotificationProfile,
    NotificationGroupProfile,  # keep if you actually use it below
    GroupNotificationProfile,  # keep if you actually use it below
)
from notifications_system.models.notification_preferences import (
    NotificationPreference,
    EventNotificationPreference,
    RoleNotificationPreference,
    UserNotificationPreference,      # keep if used elsewhere
    NotificationEventPreference,
    NotificationPreferenceGroup,
)
from notifications_system.models.broadcast_notification import (
    BroadcastNotification,
    BroadcastOverride,
)
from notifications_system.models.notification_event import NotificationEvent
from notifications_system.models.notification_group import NotificationGroup
from notifications_system.models.notifications_user_status import (
    NotificationsUserStatus,
)

from notifications_system.utils.priority_mapper import (
    get_priority_from_label,
    get_label_from_priority,
    PRIORITY_LABEL_CHOICES,
)


# --- Small helpers ----------------------------------------------------------

class NotificationPriorityMetaSerializer(serializers.Serializer):
    value = serializers.IntegerField()
    label = serializers.CharField()


# --- Core notification serializers -----------------------------------------

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializes the Notification row itself (not per-user read state).
    If you need read/pinned info, use NotificationUserStatusSerializer.
    """
    actor = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    priority_meta = serializers.SerializerMethodField()
    event_label = serializers.SerializerMethodField()
    event_namespace = serializers.SerializerMethodField()
    priority_label = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id", "website", "type", "title", "message", "link", "category",
            "event", "sent_at", "created_at", "actor",
            "payload", "rendered_title", "rendered_message", "rendered_link",
            "is_critical", "is_digest", "digest_group",
            "priority", "priority_label", "priority_meta",
            "time_ago", "event_namespace", "event_label",
        ]
        read_only_fields = ["id", "created_at", "sent_at", "actor", "time_ago", "priority_meta"]

        extra_kwargs = {
            "type": {"required": True},
            "title": {"required": True},
            "message": {"required": True},
            "event": {"required": True},
            "category": {"required": False},
            "is_critical": {"required": False},
            "is_digest": {"required": False},
            "digest_group": {"required": False},
            "priority": {"required": False},
        }

    # ---- derived fields

    def get_actor(self, obj):
        if not getattr(obj, "actor", None):
            return None
        a = obj.actor
        return {"id": a.id, "username": a.username, "email": a.email}

    def get_time_ago(self, obj):
        return f"{timesince(obj.created_at)} ago"

    def get_event_namespace(self, obj) -> str:
        # e.g. "order.assigned" -> "order"
        return (obj.event or "").split(".", 1)[0] if obj.event else ""

    def get_event_label(self, obj) -> str:
        # If EVENT_LABELS maps enum/string keys, fall back to a prettified label
        key = getattr(obj, "event", "") or ""
        return EVENT_LABELS.get(key, key.replace("_", " ").replace(".", " · ").title())

    def get_priority_label(self, obj) -> str:
        # obj.priority is an int → label
        return get_label_from_priority(obj.priority)

    def get_priority_meta(self, obj):
        return {"value": obj.priority, "label": get_label_from_priority(obj.priority)}

    # ---- validation

    def validate_type(self, value):
        # Ensure valid channel/type choice
        # TextChoices exposes `.values` (Django 4+) or `.choices`
        valid_values = getattr(NotificationType, "values", None)
        if callable(valid_values):
            valid = set(NotificationType.values)
        else:
            # fallback to choices list of tuples
            valid = {c[0] for c in NotificationType.choices}
        if value not in valid:
            raise serializers.ValidationError(f"Invalid notification type: {value}")
        return value

    def validate(self, data):
        # If client sends priority_label, convert to numeric priority
        label = data.get("priority_label")
        if label:
            data["priority"] = get_priority_from_label(label)
        return data


class NotificationUserStatusSerializer(serializers.ModelSerializer):
    """
    Per-user read/pin/priority state for a notification.
    """
    notification = NotificationSerializer(read_only=True)

    class Meta:
        model = NotificationsUserStatus
        fields = [
            "id",
            "user",
            "notification",
            "is_acknowledged",
            "is_acknowledged_at",
            "is_read",
            "read_at",
            "pinned",
            "pinned_at",
            "priority",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at",
            "is_acknowledged_at", "read_at", "pinned_at"
        ]


# --- Preferences / profiles -------------------------------------------------

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
            "channel_preferences", "user", "website",
        ]
        read_only_fields = ["id"]

class UserNotificationPreferenceSerializer(serializers.ModelSerializer):
    """User-specific notification preferences."""

    class Meta:
        model = UserNotificationPreference
        fields = [
            "id", "user", "preference_group", "website",
            "receive_email", "receive_sms", "receive_push",
            "receive_in_app", "mute_all", "digest_only",
            "muted_events", "channel_preferences",
        ]
        read_only_fields = ["id"]

class NotificationPreferencesSerializer(serializers.Serializer):
    """Serializer for updating multiple notification preferences at once."""
    preferences = UserNotificationPreferenceSerializer(many=True)

    def validate(self, data):
        if not data.get("preferences"):
            raise serializers.ValidationError("Preferences list cannot be empty.")
        return data

    def save(self, user):
        preferences_data = self.validated_data.get("preferences", [])
        updated_preferences = []

        for pref_data in preferences_data:
            pref_instance, created = UserNotificationPreference.objects.update_or_create(
                user=user,
                website=pref_data.get("website"),
                defaults={
                    "preference_group": pref_data.get("preference_group"),
                    "receive_email": pref_data.get("receive_email"),
                    "receive_sms": pref_data.get("receive_sms"),
                    "receive_push": pref_data.get("receive_push"),
                    "receive_in_app": pref_data.get("receive_in_app"),
                    "mute_all": pref_data.get("mute_all"),
                    "digest_only": pref_data.get("digest_only"),
                    "muted_events": pref_data.get("muted_events"),
                    "channel_preferences": pref_data.get("channel_preferences"),
                }
            )
            updated_preferences.append(pref_instance)

        return updated_preferences


class EventNotificationPreferenceSerializer(serializers.ModelSerializer):
    """Per-event channel toggles on a per-website basis."""
    class Meta:
        model = EventNotificationPreference
        fields = [
            "id", "event", "website",
            "email_enabled", "sms_enabled",
            "push_enabled", "in_app_enabled",
        ]
        read_only_fields = ["id"]

    # NOTE: these must live on the serializer, not inside Meta
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
            data.get("in_app_enabled"),
        ]):
            raise serializers.ValidationError(
                "At least one channel must be enabled."
            )
        return data


class NotificationEventPreferenceSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(
        source="event.name", read_only=True
    )
    event_code = serializers.CharField(
        source="event.event", read_only=True
    )

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
    group_name = serializers.CharField(
        source="group.name", read_only=True
    )

    class Meta:
        model = NotificationGroupProfile
        fields = ["id", "group", "group_name", "profile"]


# --- Broadcasts -------------------------------------------------------------

class BroadcastNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastNotification
        fields = [
            "id", "title", "message", "pinned", "require_acknowledgement",
            "dismissible", "show_in_dashboard", "send_email", "channels",
            "created_at", "updated_at", "website", "event_type", "is_active",
            "scheduled_for", "sent_at", "created_by", "is_blocking", "is_optional",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "sent_at"]


class BroadcastOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastOverride
        # Assuming your model uses `website` (not `tenant`)
        fields = [
            "id", "event_type", "force_channels",
            "title", "message", "website", "active"
        ]


# --- Groups / misc ----------------------------------------------------------

class NotificationPreferenceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreferenceGroup
        fields = [
            "id", "name", "description",
            "website", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NotificationGroupSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationGroup
        fields = [
            'id', 'name', 'description', 'website', 'website_name', 'website_domain',
            'channels', 'is_active', 'default_channel', 'default_priority',
            'is_enabled_by_default', 'created_at', 'updated_at', 'user_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        return obj.users.count()


# --- Small action payload ---------------------------------------------------

class NotificationMarkSerializer(serializers.Serializer):
    """
    Payload to mark a Notification instance as read/seen.
    NOTE: If you track reads in NotificationsUserStatus, prefer an endpoint
    that updates the NotificationsUserStatus row instead.
    """
    read = serializers.BooleanField(required=False)
    seen = serializers.BooleanField(required=False)

    def save(self, instance: Notification) -> Notification:
        read = self.validated_data.get("read")
        seen = self.validated_data.get("seen")

        # If using per-user status, you should update NotificationsUserStatus here
        # For legacy compatibility, we keep direct flags on Notification only if they exist.
        update_fields = []

        if hasattr(instance, "is_read") and read is True:
            instance.is_read = True
            instance.read_at = timezone.now()
            update_fields += ["is_read", "read_at"]

        if hasattr(instance, "is_seen") and seen is True:
            instance.is_seen = True
            instance.seen_at = timezone.now()
            update_fields += ["is_seen", "seen_at"]

        if update_fields:
            instance.save(update_fields=update_fields)
        return instance
    

class NotificationFeedItemSerializer(serializers.ModelSerializer):
    """
    A single feed row = Notification + the viewer’s state.
    """
    notification = NotificationSerializer(read_only=True)

    class Meta:
        model = NotificationsUserStatus
        fields = [
            "id",
            "notification",
            "is_read",
            "read_at",
            "is_acknowledged",
            "is_acknowledged_at",
            "pinned",
            "pinned_at",
            "priority",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at",
            "read_at", "is_acknowledged_at",
            "pinned_at"
        ]


class NotificationStatusMarkSerializer(serializers.Serializer):
    """
    Payload to update per-user state for ONE notification.
    """
    read = serializers.BooleanField(required=False)
    seen = serializers.BooleanField(required=False)  # if you track it on status, add field
    pinned = serializers.BooleanField(required=False)
    acknowledged = serializers.BooleanField(required=False)

    def save(self, instance: NotificationsUserStatus) -> NotificationsUserStatus:
        now = timezone.now()
        changed = False

        read = self.validated_data.get("read")
        if read is True and not instance.is_read:
            instance.is_read = True
            instance.read_at = now
            changed = True

        # Only update if your model has is_seen/seen_at; otherwise remove this block
        seen = self.validated_data.get("seen")
        if seen is True and hasattr(instance, "is_seen") and not instance.is_seen:
            instance.is_seen = True
            instance.seen_at = now
            changed = True

        pinned = self.validated_data.get("pinned")
        if pinned is True and not instance.pinned:
            instance.pinned = True
            instance.pinned_at = now
            changed = True
        elif pinned is False and instance.pinned:
            instance.pinned = False
            instance.pinned_at = None
            changed = True

        ack = self.validated_data.get("acknowledged")
        if ack is True and not instance.is_acknowledged:
            instance.is_acknowledged = True
            instance.is_acknowledged_at = now
            changed = True

        if changed:
            instance.save()
        return instance


class PreviewRequestSerializer(serializers.Serializer):
    """Serializer for previewing a notification event."""
    event = serializers.CharField()
    payload = serializers.JSONField(required=False, default=dict)

class NotificationStatusBulkMarkSerializer(serializers.Serializer):
    """
    Payload to update MANY notifications in one request.
    Either ids OR all_unread=True must be provided.
    """
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False, allow_empty=False
    )
    read = serializers.BooleanField(
        required=False, default=None
    )
    pinned = serializers.BooleanField(
        required=False, default=None
    )
    acknowledged = serializers.BooleanField(
        required=False, default=None
    )
    all_unread = serializers.BooleanField(
        required=False, default=False
    )

    def validate(self, data):
        if not data.get("ids") and not data.get("all_unread"):
            raise serializers.ValidationError(
                "Provide 'ids' OR set 'all_unread'=true."
            )
        return data
    
class NotificationGroupProfileSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences at the group level."""
    website_name = serializers.CharField(source='website.name', read_only=True)
    website_domain = serializers.CharField(source='website.domain', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    profile_name = serializers.CharField(source='profile.name', read_only=True)
    user_count = serializers.SerializerMethodField()
    active_channels = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationGroupProfile
        fields = [
            'id', 'name', 'website', 'website_name', 'website_domain',
            'profile', 'profile_name', 'group', 'group_name',
            'allowed_channels', 'min_priority', 'roles', 'role_slug',
            'is_active', 'is_default', 'receive_email', 'receive_in_app',
            'receive_push', 'receive_sms', 'created_at', 'updated_at',
            'user_count', 'active_channels'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        return obj.users.count()
    
    def get_active_channels(self, obj):
        return obj.get_active_channels()