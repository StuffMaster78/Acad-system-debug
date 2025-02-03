from rest_framework import serializers
from django.utils import timezone
from .models import OrderMessage, OrderMessageThread, DisputeMessage, FlaggedMessage, OrderMessageNotification, ScreenedWord


class OrderMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Order Messages, ensuring role-based visibility and filtering.
    Includes flagged message details if applicable.
    """
    sender_role = serializers.CharField(source="sender_role", read_only=True)
    sent_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    flagged_message = serializers.SerializerMethodField()

    class Meta:
        model = OrderMessage
        fields = ["id", "thread", "sender", "sender_role", "message", "sent_at",
                  "is_read", "flagged_message"]

    def get_flagged_message(self, obj):
        """Return flagged message details if the message is flagged, otherwise return an empty dictionary."""
        flagged_instance = getattr(obj, "flagged_message", None)
        if flagged_instance:
            return FlaggedMessageSerializer(flagged_instance).data
        return {}


class OrderMessageThreadSerializer(serializers.ModelSerializer):
    """
    Serializer for Order Message Threads.
    """
    class Meta:
        model = OrderMessageThread
        fields = ["id", "order", "is_active", "admin_override", "created_at"]


class OrderMessageNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Message Notifications.
    Includes expiration date for flagged notifications.
    """
    expires_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = OrderMessageNotification
        fields = ["id", "recipient", "message", "notification_text", "is_read", "created_at", "expires_at"]


class ScreenedWordSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin-Controlled Banned Words.
    """
    class Meta:
        model = ScreenedWord
        fields = ["id", "word"]


class FlaggedMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for flagged messages, allowing admin review.
    """
    order_id = serializers.CharField(source="order_message.thread.order.id", read_only=True)
    sender_username = serializers.CharField(source="order_message.sender.username", read_only=True)
    sanitized_message = serializers.CharField(source="order_message.message", read_only=True)
    reviewed_by = serializers.CharField(source="reviewed_by.username", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)  # Human-readable category

    class Meta:
        model = FlaggedMessage
        fields = ["id", "order_id", "sender_username", "sanitized_message", "flagged_reason",
                  "category", "category_display", "flagged_at", "admin_comment", "reviewed_by",
                  "reviewed_at", "is_unblocked"]


class AdminEditFlaggedMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for admins to edit flagged messages if needed.
    """
    last_edited_by = serializers.SerializerMethodField()
    last_edited_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = FlaggedMessage
        fields = ["id", "admin_comment", "last_edited_by", "last_edited_at"]

    def get_last_edited_by(self, obj):
        """Returns the username of the last admin who edited, or None if not edited."""
        return obj.last_edited_by.username if obj.last_edited_by else None

    def update(self, instance, validated_data):
        instance.admin_comment = validated_data.get("admin_comment", instance.admin_comment)
        instance.last_edited_by = self.context["request"].user
        instance.last_edited_at = timezone.now()
        instance.save()
        return instance


class AdminReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to review and unblock a message.
    """
    reviewed_by = serializers.CharField(source="reviewed_by.username", read_only=True)
    reviewed_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = FlaggedMessage
        fields = ["id", "admin_comment", "reviewed_by", "reviewed_at", "is_unblocked"]

    def update(self, instance, validated_data):
        """
        Update flagged message with review details.
        """
        instance.admin_comment = validated_data.get("admin_comment", instance.admin_comment)
        instance.reviewed_by = self.context["request"].user
        instance.reviewed_at = timezone.now()
        instance.is_unblocked = True
        instance.save()
        return instance
    

class DisputeMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for handling dispute messages.
    """
    sender_role = serializers.CharField(source="sender_role", read_only=True)
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    order_id = serializers.CharField(source="order_message.thread.order.id", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = DisputeMessage
        fields = ["id", "order_id", "sender_username", "sender_role", "message", "status", "status_display",
                  "category", "category_display", "resolution_comment", "resolved_at", "created_at"]
