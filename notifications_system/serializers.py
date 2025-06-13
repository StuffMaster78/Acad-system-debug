from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
   """
    Serializer for displaying notifications in frontend apps.
    Includes key fields needed to render properly.
    """
   is_unread = serializers.SerializerMethodField()
   relative_time = serializers.SerializerMethodField()
   ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="IDs of notifications to mark as read."
    )

   class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "message",
            "category",
            "is_read",
            "is_unread",
            "status",
            "sent_at",
            "created_at",
            "relative_time",
        ]
        read_only_fields = fields

def get_is_unread(self, obj):
    return not obj.is_read

def get_relative_time(self, obj):
    from django.utils.timesince import timesince
    return timesince(obj.created_at) + " ago"

class NotificationMarkReadSerializer(serializers.Serializer):
    """
    Serializer for marking notifications as read.
    
    This serializer is used in the `POST` request to the 
    'mark_as_read' endpoint, where users specify a list of 
    notification IDs to mark as read.

    Fields:
    - ids (List[int]): A list of notification IDs that need to be marked as read. 
      Each ID corresponds to a notification in the database.

    Example:
    {
        "ids": [1, 2, 3]
    }

    Returns:
    - The number of notifications that were successfully marked as read.
    """
    
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="List of notification IDs to mark as read."
    )
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



        