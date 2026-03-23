from __future__ import annotations

from rest_framework import serializers

from notifications_system.models.notifications import Notification
from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.models.user_notification_meta import UserNotificationMeta


class NotificationSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    is_pinned = serializers.SerializerMethodField()
    is_acknowledged = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'event_key', 'category', 'priority',
            'title', 'message', 'subject',
            'channels', 'status',
            'is_read', 'is_pinned', 'is_acknowledged',
            'is_critical', 'is_digest', 'is_broadcast',
            'digest_group', 'expires_at', 'sent_at',
            'created_at', 'time_ago',
        ]
        read_only_fields = fields

    def _get_user_status(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        if not hasattr(request, '_notif_status_cache'):
            request._notif_status_cache = {}
        key = f'_notif_status_{obj.id}'
        if key not in request._notif_status_cache:
            try:
                request._notif_status_cache[key] = (
                    NotificationsUserStatus.objects.get(
                        notification=obj,
                        user=request.user,
                    )
                )
            except NotificationsUserStatus.DoesNotExist:
                request._notif_status_cache[key] = None
        return request._notif_status_cache[key]

    def get_title(self, obj) -> str:
        return (obj.rendered or {}).get('title', '')

    def get_message(self, obj) -> str:
        return (obj.rendered or {}).get('message', '')

    def get_subject(self, obj) -> str:
        return (obj.rendered or {}).get('subject', '')

    def get_is_read(self, obj) -> bool:
        status = self._get_user_status(obj)
        return status.is_read if status else False

    def get_is_pinned(self, obj) -> bool:
        status = self._get_user_status(obj)
        return status.is_pinned if status else False

    def get_is_acknowledged(self, obj) -> bool:
        status = self._get_user_status(obj)
        return status.is_acknowledged if status else False

    def get_time_ago(self, obj) -> str:
        from django.utils import timezone
        diff = int((timezone.now() - obj.created_at).total_seconds())
        if diff < 60:    return 'just now'
        if diff < 3600:  return f"{diff // 60}m ago"
        if diff < 86400: return f"{diff // 3600}h ago"
        if diff < 604800: return f"{diff // 86400}d ago"
        return obj.created_at.strftime('%b %d')


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight — used for the paginated feed list."""
    title = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    is_pinned = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'event_key', 'category', 'priority',
            'title', 'message',
            'is_read', 'is_pinned', 'is_critical',
            'created_at', 'time_ago',
        ]
        read_only_fields = fields

    def _get_status(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        cache = getattr(request, '_notif_status_cache', {})
        return cache.get(f'_notif_status_{obj.id}')

    def get_title(self, obj) -> str:
        return (obj.rendered or {}).get('title', '')

    def get_message(self, obj) -> str:
        msg = (obj.rendered or {}).get('message', '')
        return msg[:120] + '…' if len(msg) > 120 else msg

    def get_is_read(self, obj) -> bool:
        status = self._get_status(obj)
        return status.is_read if status else False

    def get_is_pinned(self, obj) -> bool:
        status = self._get_status(obj)
        return status.is_pinned if status else False

    def get_time_ago(self, obj) -> str:
        from django.utils import timezone
        diff = int((timezone.now() - obj.created_at).total_seconds())
        if diff < 60:    return 'just now'
        if diff < 3600:  return f"{diff // 60}m ago"
        if diff < 86400: return f"{diff // 3600}h ago"
        if diff < 604800: return f"{diff // 86400}d ago"
        return obj.created_at.strftime('%b %d')


class NotificationsUserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationsUserStatus
        fields = [
            'id', 'notification', 'is_read', 'read_at',
            'is_acknowledged', 'acknowledged_at',
            'is_pinned', 'pinned_at', 'priority',
        ]
        read_only_fields = fields


class UserNotificationMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationMeta
        fields = [
            'unread_count', 'last_seen_at',
            'last_emailed_at', 'last_notified_at',
        ]
        read_only_fields = fields