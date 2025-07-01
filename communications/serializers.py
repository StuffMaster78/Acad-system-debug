from rest_framework import serializers
from django.utils import timezone
from .models import (
    CommunicationMessage, CommunicationThread,
    DisputeMessage, FlaggedMessage,
    CommunicationNotification, ScreenedWord,
    CommunicationLog, MessageReadReceipt,
    WebSocketAuditLog, SystemAlert
)
from users.serializers import SimpleUserSerializer
from users.models import UserProfile
from communications.utils import extract_first_link
from communications.models import MessageType
from communications.utils import generate_preview_metadata
from django.db import models
from django.contrib.postgres.fields import JSONField 
import mimetypes
import os

class CommunicationThreadSerializer(serializers.ModelSerializer):
    participants = SimpleUserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationThread
        fields = [
            "id",
            "order",
            "is_active",
            "admin_override",
            "participants",
            "created_at",
            "updated_at",
            "last_message"
        ]
        read_only_fields = fields

    def get_last_message(self, obj):
        """
        Get the last non-deleted message in the thread.
        Returns None if no messages are present.
        """
        last = obj.messages.filter(is_deleted=False).order_by("-sent_at").first()
        if last:
            return CommunicationMessageSerializer(last).data
        return None
    
    def get_unread_count(self, obj):
        """
        Get the count of unread messages for the current user in this thread.
        """
        user = self.context["request"].user
        return obj.messages.exclude(read_by=user).count()


class MessageAttachmentSerializer(serializers.Serializer):
    file = serializers.FileField(read_only=True)
    filename = serializers.SerializerMethodField()
    filetype = serializers.SerializerMethodField()
    filesize = serializers.SerializerMethodField()
    is_image = serializers.SerializerMethodField()
    extension = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()

    def get_filename(self, obj):
        return os.path.basename(obj.name) if obj else None

    def get_filetype(self, obj):
        mime_type, _ = mimetypes.guess_type(obj.name)
        return mime_type or "application/octet-stream"

    def get_extension(self, obj):
        return os.path.splitext(obj.name)[1].lower().strip(".") if obj else None

    def get_filesize(self, obj):
        return obj.size if obj else 0

    def get_is_image(self, obj):
        mime_type = self.get_filetype(obj)
        return mime_type.startswith("image/")

    def get_preview_url(self, obj):
        request = self.context.get("request")
        if obj and request:
            return request.build_absolute_uri(obj.url)
        return None
    
class CommunicationMessageSerializer(serializers.ModelSerializer):
    sender = SimpleUserSerializer(read_only=True)
    sender_role = serializers.CharField(read_only=True)
    recipient = SimpleUserSerializer(read_only=True)
    reply_to_id = serializers.PrimaryKeyRelatedField(
        queryset=CommunicationMessage.objects.all(),
        source="reply_to",
        required=False,
        allow_null=True
    )
    attachment = MessageAttachmentSerializer(source="attachment_file", read_only=True)

    is_sender = serializers.SerializerMethodField()
    is_system = serializers.SerializerMethodField()
    link_url = serializers.URLField(read_only=True)
    link_preview = serializers.SerializerMethodField()
    message_type = serializers.ChoiceField(
        choices=MessageType.choices, default=MessageType.TEXT
    )
    is_flagged = serializers.BooleanField(read_only=True)
    is_hidden = serializers.BooleanField(read_only=True)
    contains_link = serializers.BooleanField(read_only=True)
    is_link_approved = serializers.BooleanField(read_only=True)
    link_domain = serializers.CharField(read_only=True)
    is_read = serializers.SerializerMethodField()
    sent_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    flagged_message = serializers.SerializerMethodField()
    read_receipts = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    link_preview_json = serializers.JSONField(read_only=True)

    class Meta:
        model = CommunicationMessage
        fields = [
            "id", "thread", "sender", "sender_role", "recipient", "message",
            "reply_to_id", "message_type", "link_url", "link_domain",
            "is_flagged", "is_hidden", "contains_link", "is_link_approved",
            "is_read", "sent_at", "flagged_message", "read_receipts", "attachment",
            "unread_count", "is_system"
        ]
        read_only_fields = [
            "id", "thread", "sender",
            "sender_role", "recipient", "sent_at"
        ]

    def get_is_read(self, obj):
        """
        Check if the message has been read by the current user.
        """
        user = self.context["request"].user
        return obj.read_by.filter(id=user.id).exists()

    def get_flagged_message(self, obj):
        flagged_instance = getattr(obj, "flagged_message", None)
        return FlaggedMessageSerializer(flagged_instance).data if flagged_instance else {}
    
    def get_is_system(self, obj):
        return obj.message_type == MessageType.SYSTEM
    
    def get_unread_count(self, obj):
        user = self.context["request"].user
        return 0 if user in obj.read_by.all() else 1
    
    def get_is_sender(self, obj):
        """ Check if the current user is the sender of the message. """
        request_user = self.context.get("request", {}).user
        return bool(request_user and obj.sender and obj.sender == request_user)
    
    def get_link_preview(self, obj):
        return obj.link_preview_json if obj.link_preview_json else None
    
    def get_read_receipts(self, obj):
        """ Retrieve read receipts for the message.
        Only visible to the sender of the message.
        """
        request = self.context.get("request")
        if not request or not request.user:
            return []

        # Only show receipts to sender
        if obj.sender != request.user:
            return []

        # Return list of readers and read times
        return [
            {
                "username": receipt.user.username,
                "role": receipt.user.profile.role,
                "self": receipt.user == request.user,
                "read_at": receipt.read_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for receipt in obj.messagereadreceipt_set.select_related("user__profile")
        ]


class CreateCommunicationMessageSerializer(serializers.Serializer):
    """"
    Serializer for creating a new communication message.
    This is used for sending messages in a thread.
    """
    thread = serializers.UUIDField()
    recipient_id = serializers.UUIDField()
    message = serializers.CharField()
    reply_to_id = serializers.UUIDField(required=False, allow_null=True)


    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value
    


    def validate(self, data):
        """ Validate the entire message data.
        - Ensure the thread exists and is active.
        - Ensure the recipient is not the sender.
        - Autodetect links in the message.
        """
        thread = CommunicationThread.objects.filter(id=data["thread"]).first()
        if thread and not thread.is_active:
            raise serializers.ValidationError(
                "Thread is no longer active."
            )
        
        request = self.context.get("request")
        if data.get("message_type") == MessageType.SYSTEM:
            raise serializers.ValidationError(
                "System messages cannot be created manually."
            )
        if not thread:
            raise serializers.ValidationError("Thread does not exist.")
        if not thread.participants.filter(id=data["recipient_id"]).exists():
            raise serializers.ValidationError(
                "Recipient is not a participant in this thread."
            )
        if not thread.participants.filter(id=request.user.id).exists():
            raise serializers.ValidationError(
                "You are not a participant in this thread."
            )
        if "reply_to_id" in data and data["reply_to_id"]:
            reply_to = CommunicationMessage.objects.filter(id=data["reply_to_id"]).first()
            if not reply_to or reply_to.thread != thread:
                raise serializers.ValidationError(
                    "Reply-to message does not belong to this thread."
                )
            data["reply_to"] = reply_to
        else:
            data["reply_to"] = None
        # Validate recipient ID
        data["recipient_id"] = self.validate_recipient_id(data["recipient_id"])
        # Ensure recipient is not the sender
        user = request.user
        if str(data["recipient_id"]) == str(user.id):
            raise serializers.ValidationError("Cannot send message to yourself.")
        
        # Autodetect links
        link = extract_first_link(data["message"])
        if link:
            data["link"] = link
            try:
                domain = link.split("/")[2]
                data["link_domain"] = domain if domain else None
            except IndexError:
                data["link_domain"] = None
        return data
    
    def validate_recipient_id(self, value):
        """ 
        Ensure the recipient is not the sender.
        """
        user = self.context["request"].user
        if str(value) == str(user.id):
            raise serializers.ValidationError("Cannot send message to yourself.")
        return value


    

class CommunicationLogSerializer(serializers.ModelSerializer):
    """
    Serializer for communication log entries (auditing).
    """
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = CommunicationLog
        fields = [
            "id", "user_username", "order", "action",
            "details", "created_at"
        ]
        read_only_fields = ["id", "user_username", "created_at"]
    
class MessageModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationMessage
        fields = ["is_link_approved", "is_hidden"]
        read_only_fields = ["is_hidden"]



class ScreenedWordSerializer(serializers.ModelSerializer):
    """
    Serializer for admin-configured screened (banned) words.
    """
    class Meta:
        model = ScreenedWord
        fields = ["id", "word"]
        read_only_fields = ["id"]

class FlaggedMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for flagged messages for admin review.
    """
    order_id = serializers.CharField(
        source="message.thread.order.id", read_only=True
    )
    sender_username = serializers.CharField(
        source="message.sender.username", read_only=True
    )
    sanitized_message = serializers.CharField(
        source="message.message", read_only=True
    )
    reviewed_by = serializers.CharField(
        source="reviewed_by.username", read_only=True
    )
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = FlaggedMessage
        fields = [
            "id", "order_id", "sender_username", "sanitized_message",
            "flagged_reason", "category", "category_display",
            "flagged_at", "admin_comment", "reviewed_by",
            "reviewed_at", "is_unblocked"
        ]
        read_only_fields = [
            "id", "order_id", "sender_username", "sanitized_message",
            "flagged_at", "reviewed_by", "reviewed_at", "category_display"
        ]
    def validate(self, attrs):
        """
        Ensure that the category is valid and not empty.
        """
        if not attrs.get("category"):
            raise serializers.ValidationError("Category cannot be empty.")
        return attrs
    

class AdminEditFlaggedMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for admins to leave a comment/edit on a flagged message.
    """
    last_edited_by = serializers.SerializerMethodField()
    last_edited_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", read_only=True
    )

    class Meta:
        model = FlaggedMessage
        fields = ["id", "admin_comment", "last_edited_by", "last_edited_at"]

    def get_last_edited_by(self, obj):
        return obj.last_edited_by.username if obj.last_edited_by else None

    def update(self, instance, validated_data):
        instance.admin_comment = validated_data.get(
            "admin_comment", instance.admin_comment
        )
        instance.last_edited_by = self.context["request"].user
        instance.last_edited_at = timezone.now()
        instance.save()
        return instance

class AdminReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to review and unblock a flagged message.
    """
    reviewed_by = serializers.CharField(
        source="reviewed_by.username", read_only=True
    )
    reviewed_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", read_only=True
    )

    class Meta:
        model = FlaggedMessage
        fields = [
            "id", "admin_comment", "reviewed_by",
            "reviewed_at", "is_unblocked"
        ]

    def update(self, instance, validated_data):
        instance.admin_comment = validated_data.get(
            "admin_comment", instance.admin_comment
        )
        instance.reviewed_by = self.context["request"].user
        instance.reviewed_at = timezone.now()
        instance.is_unblocked = True
        instance.save()
        return instance

class DisputeMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for handling dispute messages.
    """
    message = serializers.CharField(required=True)
    sender_role = serializers.CharField(read_only=True)
    sender_username = serializers.CharField(
        source="sender.username", read_only=True
    )
    order_id = serializers.CharField(
        source="order_message.thread.order.id", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = DisputeMessage
        fields = [
            "id", "order_id", "sender_username", "sender_role",
            "message", "status", "status_display", "category",
            "category_display", "resolution_comment",
            "resolved_at", "created_at"
        ]
        read_only_fields = [
            "id", "order_id", "sender_username", "sender_role",
            "status_display", "category_display", "resolved_at", "created_at"
        ]
    def validate(self, attrs):
        """
        Ensure that the message is not empty and the status is valid.
        """
        if not attrs.get("message", "").strip():
            raise serializers.ValidationError("Message cannot be empty.")
        
        if attrs.get("status") not in dict(DisputeMessage.STATUS_CHOICES):
            raise serializers.ValidationError("Invalid dispute status.")
        
        return attrs
    
class CommunicationNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for communication notifications.
    """
    recipient_username = serializers.CharField(
        source="recipient.username", read_only=True
    )
    message_preview = serializers.CharField(
        source="message.message", read_only=True
    )
    read_at = serializers.SerializerMethodField()


    class Meta:
        model = CommunicationNotification
        fields = [
            "id", "recipient", "recipient_username",
            "message", "message_preview", "notification_text",
            "is_read", "created_at", "read_at"
        ]
        read_only_fields = ["id", "recipient_username", "message_preview", "read_at"]


    def validate(self, attrs):
        """
        Ensure that the notification text is not empty.
        """
        if not attrs.get("notification_text", "").strip():
            raise serializers.ValidationError("Notification text cannot be empty.")
        return attrs
    

class MinimalMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationMessage
        fields = ["id", "message", "sent_at"]


class ThreadParticipantSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["user", "role"]

class NotificationMarkReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationNotification
        fields = ["is_read"]


class MessageReadSerializer(serializers.ModelSerializer):
    """
    Serializer to mark a communication message as read.
    """
    is_read = serializers.SerializerMethodField()
    read_by = SimpleUserSerializer(many=True, read_only=True)
    read_at = serializers.SerializerMethodField()
    was_read_recently = serializers.SerializerMethodField()


    class Meta:
        model = CommunicationMessage
        fields = ["id", "is_read", "read_by", "read_at", "was_read_recently"]
        read_only_fields = ["id", "read_by", "read_at"]

    def get_read_at(self, obj):
        """
        Get the read timestamp for the current user.
        Returns None if the user has not read the message.
    """
        user = self.context["request"].user
        receipt = obj.messagereadreceipt_set.filter(user=user).first()
        return receipt.read_at if receipt else None


    def get_was_read_recently(self, obj):
        """
        Check if the message was read within the last hour.
        """
        read_at = self.get_read_at(obj)
        if not read_at:
            return False
        return (timezone.now() - read_at).total_seconds() < 3600

    def update(self, instance, validated_data):
        user = self.context["request"].user
        is_impersonated = getattr(user, "is_impersonated", False)

        if is_impersonated:
            raise serializers.ValidationError(
                "Cannot mark message as read while impersonating."
            )

        if instance.recipient and instance.recipient != user:
            raise serializers.ValidationError(
                "You are not the intended recipient of this message."
            )
        
        # Already marked?
        if MessageReadReceipt.objects.filter(message=instance, user=user).exists():
            return instance
        
            # Short view prevention
        if instance.sent_at and (timezone.now() - instance.sent_at).total_seconds() < 2:
            raise serializers.ValidationError("Viewed too briefly.")

        # Log the read event
        sender = instance.sender  # this is the writer
        recipient = user          # this is the client
        
        _, created = MessageReadReceipt.objects.create(
            message=instance,
            user=user,
            read_at=timezone.now()
        )
        if created:
            CommunicationLog.objects.create(
                user=recipient,
                order=instance.thread.order,
                action="read_message",
                details=f"{recipient.get_display_name()} read message #{instance.id} from {sender.get_display_name()}"
            )

        return instance

    

class NotificationReadSerializer(serializers.ModelSerializer):
    """
    Serializer to mark a communication notification as read.
    """
    class Meta:
        model = CommunicationNotification
        fields = ["id", "is_read"]

class MyInboxThreadSerializer(serializers.ModelSerializer):
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationThread
        fields = [
            "id", "thread_type", "order", "unread_count",
            "last_message_preview", "updated_at"
        ]

    def get_last_message_preview(self, obj):
        msg = obj.messages.order_by("-sent_at").first()
        if not msg:
            return ""
        if msg.message_type == MessageType.SYSTEM:
            return f"[System] {msg.message[:50]}..."
        return msg.message[:50] + "..."


    def get_unread_count(self, obj):
        user = self.context["request"].user
        return obj.messages.exclude(read_by=user).count()
    


class WebSocketAuditLogSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    thread_id = serializers.CharField(source="thread.id", read_only=True)

    class Meta:
        model = WebSocketAuditLog
        fields = [
            "id", "user", "thread_id", "action", "payload", "created_at"
        ]
        read_only_fields = fields