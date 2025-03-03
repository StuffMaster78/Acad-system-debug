from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""

    user = serializers.StringRelatedField()  # Returns the username instead of ID

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "type",
            "title",
            "message",
            "is_read",
            "status",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "user", "sent_at", "created_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model."""

    class Meta:
        model = NotificationPreference
        fields = [
            "id",
            "user",
            "receive_email",
            "receive_sms",
            "receive_push",
            "receive_in_app",
        ]
        read_only_fields = ["id", "user"]