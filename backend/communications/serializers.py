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
            "last_message",
            "unread_count"
        ]
        read_only_fields = ["id", "is_active", "admin_override", "participants", "created_at", "updated_at", "last_message", "unread_count"]

    def get_last_message(self, obj):
        """
        Get the last non-deleted message in the thread.
        Returns None if no messages are present.
        Optimized to use prefetched messages if available.
        Admin/superadmin can see all messages regardless of visibility rules.
        """
        request = self.context.get("request")
        user = request.user if request else None
        user_role = getattr(user, "role", None) if user else None
        
        # Admin/superadmin can see all messages (including those between other recipients)
        if user_role in {"admin", "superadmin"}:
            # Use prefetched messages if available
            if hasattr(obj, '_prefetched_objects_cache') and 'messages' in obj._prefetched_objects_cache:
                messages = [m for m in obj._prefetched_objects_cache['messages'] if not m.is_deleted]
                if messages:
                    last = sorted(messages, key=lambda m: m.sent_at, reverse=True)[0]
                    return CommunicationMessageSerializer(last, context=self.context).data
                return None
            
            # Fallback to database query
            last = obj.messages.filter(is_deleted=False).order_by("-sent_at").first()
            if last:
                return CommunicationMessageSerializer(last, context=self.context).data
            return None
        
        # For other users, use prefetched messages if available
        if hasattr(obj, '_prefetched_objects_cache') and 'messages' in obj._prefetched_objects_cache:
            messages = [m for m in obj._prefetched_objects_cache['messages'] if not m.is_deleted]
            if messages:
                # Sort by sent_at descending and get first
                last = sorted(messages, key=lambda m: m.sent_at, reverse=True)[0]
                return CommunicationMessageSerializer(last, context=self.context).data
            return None
        
        # Fallback to database query if not prefetched
        last = obj.messages.filter(is_deleted=False).order_by("-sent_at").first()
        if last:
            return CommunicationMessageSerializer(last, context=self.context).data
        return None
    
    def get_unread_count(self, obj):
        """
        Get the count of unread messages for the current user in this thread.
        Only counts messages that are visible to the user (matches get_visible_messages logic).
        This ensures the count matches the actual visible messages.
        """
        request = self.context.get("request")
        if not request or not request.user:
            return 0
        user = request.user
        
        # Get visible messages using the same logic as get_visible_messages
        from communications.services.messages import MessageService
        visible_messages = MessageService.get_visible_messages(user, obj)
        
        # Count unread messages from visible messages only
        unread_count = visible_messages.exclude(read_by=user).count()
        
        return unread_count


class CreateCommunicationThreadSerializer(serializers.Serializer):
    """Serializer for creating a new communication thread."""
    order = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Order ID for this thread (optional for general threads)"
    )
    website = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Website ID (optional, will be derived from order if not provided)"
    )
    participants = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text="List of participant user IDs"
    )
    thread_type = serializers.ChoiceField(
        choices=CommunicationThread.THREAD_TYPE_CHOICES,
        default="order",
        required=False
    )

    def validate_order(self, value):
        """Validate order exists and is accessible."""
        if value is None:
            return None
        from orders.models import Order
        try:
            order = Order.objects.get(id=value)
            return order
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order does not exist.")
    
    def validate_website(self, value):
        """Validate website exists if provided."""
        if value is None:
            return None
        from websites.models import Website
        try:
            website = Website.objects.get(id=value)
            return website
        except Website.DoesNotExist:
            raise serializers.ValidationError("Website does not exist.")
    
    def validate_participants(self, value):
        """Validate participants exist."""
        if not value:
            return []
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        validated_participants = []
        for user_id in value:
            try:
                user = User.objects.get(id=user_id)
                validated_participants.append(user)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with ID {user_id} does not exist.")
        
        return validated_participants


class MessageAttachmentSerializer(serializers.Serializer):
    file = serializers.FileField(read_only=True)
    filename = serializers.SerializerMethodField()
    filetype = serializers.SerializerMethodField()
    filesize = serializers.SerializerMethodField()
    is_image = serializers.SerializerMethodField()
    extension = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()

    def _has_file(self, obj):
        """Check if the attachment field has a file associated with it."""
        if not obj:
            return False
        try:
            # Check if file exists and has a name
            return bool(obj.name) and obj.storage.exists(obj.name)
        except (AttributeError, ValueError):
            return False

    def get_filename(self, obj):
        if not self._has_file(obj):
            return None
        try:
            return os.path.basename(obj.name)
        except (AttributeError, ValueError):
            return None

    def get_filetype(self, obj):
        if not self._has_file(obj):
            return None
        try:
            mime_type, _ = mimetypes.guess_type(obj.name)
            return mime_type or "application/octet-stream"
        except (AttributeError, ValueError):
            return None

    def get_extension(self, obj):
        if not self._has_file(obj):
            return None
        try:
            return os.path.splitext(obj.name)[1].lower().strip(".") if obj.name else None
        except (AttributeError, ValueError):
            return None

    def get_filesize(self, obj):
        if not self._has_file(obj):
            return 0
        try:
            return obj.size if obj else 0
        except (AttributeError, ValueError):
            return 0

    def get_is_image(self, obj):
        if not self._has_file(obj):
            return False
        try:
            mime_type = self.get_filetype(obj)
            return mime_type and mime_type.startswith("image/")
        except (AttributeError, ValueError):
            return False

    def get_preview_url(self, obj):
        if not self._has_file(obj):
            return None
        request = self.context.get("request")
        try:
            if obj and request:
                return request.build_absolute_uri(obj.url)
        except (AttributeError, ValueError):
            pass
        return None
    
from django.contrib.auth import get_user_model


class CommunicationMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    sender_role = serializers.CharField(read_only=True)
    recipient = serializers.SerializerMethodField()
    # Explicit recipient role for frontend routing/tab logic (null-safe)
    recipient_role = serializers.SerializerMethodField()
    sender_display_name = serializers.SerializerMethodField()
    recipient_display_name = serializers.SerializerMethodField()
    reply_to_id = serializers.PrimaryKeyRelatedField(
        queryset=CommunicationMessage.objects.all(),
        source="reply_to",
        required=False,
        allow_null=True
    )
    attachment = serializers.SerializerMethodField()

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
    sent_at = serializers.DateTimeField(read_only=True)  # ISO format for timezone-aware display
    flagged_message = serializers.SerializerMethodField()
    read_receipts = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    link_preview_json = serializers.JSONField(read_only=True)
    reactions = serializers.SerializerMethodField()
    is_previous_writer_message = serializers.SerializerMethodField()
    previous_writer_label = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationMessage
        fields = [
            "id", "thread", "sender", "sender_role", "recipient", "recipient_role", "message",
            "sender_display_name", "recipient_display_name",
            "reply_to_id", "message_type", "link_url", "link_domain",
            "is_flagged", "is_hidden", "contains_link", "is_link_approved",
            "is_read", "sent_at", "flagged_message", "read_receipts", "attachment",
            "unread_count", "is_system", "is_sender", "link_preview", "link_preview_json",
            "reactions", "is_previous_writer_message", "previous_writer_label"
        ]
        read_only_fields = [
            "id", "thread", "sender",
            "sender_role", "recipient", "sent_at"
        ]

    def get_sender(self, obj):
        """Return anonymized sender info based on viewer's role."""
        request = self.context.get("request")
        if not request or not request.user:
            return SimpleUserSerializer(obj.sender).data
        
        viewer = request.user
        viewer_role = getattr(viewer, "role", None)
        sender_role = obj.sender_role
        
        # Staff (admin, superadmin, support, editor) can see all names
        if viewer_role in {"admin", "superadmin", "support", "editor"}:
            return SimpleUserSerializer(obj.sender).data
        
        # Clients see anonymized writer info
        if viewer_role == "client":
            if sender_role == "writer":
                return {
                    "id": obj.sender.id,
                    "username": f"Writer #{obj.sender.id}",
                    "email": None
                }
            elif sender_role in {"admin", "superadmin", "support"}:
                return {
                    "id": obj.sender.id,
                    "username": "Support",
                    "email": None
                }
            elif sender_role == "editor":
                return {
                    "id": obj.sender.id,
                    "username": "Editor",
                    "email": None
                }
        
        # Writers see anonymized client info
        if viewer_role == "writer":
            if sender_role == "client":
                return {
                    "id": obj.sender.id,
                    "username": "Client",
                    "email": None
                }
            elif sender_role in {"admin", "superadmin", "support"}:
                return {
                    "id": obj.sender.id,
                    "username": "Support",
                    "email": None
                }
            elif sender_role == "editor":
                return {
                    "id": obj.sender.id,
                    "username": "Editor",
                    "email": None
                }
        
        # Default: return full info
        return SimpleUserSerializer(obj.sender).data
    
    def get_recipient(self, obj):
        """Return anonymized recipient info based on viewer's role."""
        # Guard against any unexpected null recipients
        if not getattr(obj, "recipient", None):
          return None
        request = self.context.get("request")
        if not request or not request.user:
            return SimpleUserSerializer(obj.recipient).data
        
        viewer = request.user
        viewer_role = getattr(viewer, "role", None)
        recipient_role = getattr(obj.recipient, "role", None)
        
        # Staff can see all names
        if viewer_role in {"admin", "superadmin", "support", "editor"}:
            return SimpleUserSerializer(obj.recipient).data
        
        # Clients see anonymized writer info
        if viewer_role == "client":
            if recipient_role == "writer":
                return {
                    "id": obj.recipient.id,
                    "username": f"Writer #{obj.recipient.id}",
                    "email": None
                }
            elif recipient_role in {"admin", "superadmin", "support"}:
                return {
                    "id": obj.recipient.id,
                    "username": "Support",
                    "email": None
                }
            elif recipient_role == "editor":
                return {
                    "id": obj.recipient.id,
                    "username": "Editor",
                    "email": None
                }
        
        # Writers see anonymized client info
        if viewer_role == "writer":
            if recipient_role == "client":
                return {
                    "id": obj.recipient.id,
                    "username": "Client",
                    "email": None
                }
            elif recipient_role in {"admin", "superadmin", "support"}:
                return {
                    "id": obj.recipient.id,
                    "username": "Support",
                    "email": None
                }
            elif recipient_role == "editor":
                return {
                    "id": obj.recipient.id,
                    "username": "Editor",
                    "email": None
                }
        
        # Default: return full info
        return SimpleUserSerializer(obj.recipient).data

    def get_is_previous_writer_message(self, obj):
        request = self.context.get("request")
        if not request or not request.user:
            return False
        viewer = request.user
        if getattr(viewer, "role", None) != "writer":
            return False
        thread = getattr(obj, "thread", None)
        order = getattr(thread, "order", None) if thread else None
        if not order or not getattr(order, "assigned_writer_id", None):
            return False
        if obj.sender_role != "writer":
            return False
        return obj.sender_id != order.assigned_writer_id

    def get_previous_writer_label(self, obj):
        if self.get_is_previous_writer_message(obj):
            return "Previous writer"
        return None
    
    def get_recipient_role(self, obj):
        """Return the raw recipient role for routing/tab logic."""
        recipient = getattr(obj, "recipient", None)
        return getattr(recipient, "role", None) if recipient else None
    
    def get_sender_display_name(self, obj):
        """Get display name for sender (anonymized if needed)."""
        sender_data = self.get_sender(obj)
        return sender_data.get("username", "Unknown")
    
    def get_recipient_display_name(self, obj):
        """Get display name for recipient (anonymized if needed)."""
        recipient_data = self.get_recipient(obj)
        return recipient_data.get("username", "Unknown")
    
    def get_is_read(self, obj):
        """
        Check if the message has been read by the current user.
        """
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        user = request.user
        return obj.read_by.filter(id=user.id).exists()

    def get_flagged_message(self, obj):
        flagged_instance = getattr(obj, "flagged_message", None)
        return FlaggedMessageSerializer(flagged_instance).data if flagged_instance else {}
    
    def get_is_system(self, obj):
        return obj.message_type == MessageType.SYSTEM
    
    def get_unread_count(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return 1  # Default to unread if no user context
        user = request.user
        return 0 if user in obj.read_by.all() else 1
    
    def get_is_sender(self, obj):
        """ Check if the current user is the sender of the message. """
        request_user = self.context.get("request", {}).user
        return bool(request_user and obj.sender and obj.sender == request_user)
    
    def get_attachment(self, obj):
        """Safely serialize attachment, returning None if file doesn't exist."""
        if not obj.attachment:
            return None
        
        # Check if the file actually exists
        try:
            if not obj.attachment.name or not obj.attachment.storage.exists(obj.attachment.name):
                return None
        except (AttributeError, ValueError):
            return None
        
        # Serialize the attachment
        return MessageAttachmentSerializer(obj.attachment, context=self.context).data
    
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
        # We no longer have a generic `profile` relation; `role` lives directly on `User`.
        # Use `select_related("user")` only to avoid invalid join on non-existent `profile`.
        return [
            {
                "username": receipt.user.username,
                "role": getattr(receipt.user, "role", None),
                "self": receipt.user == request.user,
                "read_at": receipt.read_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for receipt in obj.messagereadreceipt_set.select_related("user")
        ]
    
    def get_reactions(self, obj):
        """Get all reactions for this message grouped by reaction type."""
        from collections import defaultdict
        
        reactions_data = defaultdict(list)
        for reaction in obj.reactions.select_related('user').all():
            reactions_data[reaction.reaction].append({
                'user_id': reaction.user.id,
                'username': reaction.user.username,
                'created_at': reaction.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Convert to list format: [{'reaction': '👍', 'users': [...]}, ...]
        return [
            {
                'reaction': reaction,
                'count': len(users),
                'users': users
            }
            for reaction, users in reactions_data.items()
        ]


User = get_user_model()


class CreateCommunicationMessageSerializer(serializers.Serializer):
    """"
    Serializer for creating a new communication message.
    This is used for sending messages in a thread.
    """
    recipient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        help_text="Recipient user ID - must be selected by the sender"
    )
    message = serializers.CharField(required=True)
    reply_to = serializers.IntegerField(
        required=False,
        allow_null=True
    )
    message_type = serializers.ChoiceField(
        choices=MessageType.choices,
        default=MessageType.TEXT,
        required=False
    )


    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value
    


    def validate_recipient(self, value):
        """Validate recipient is not the sender."""
        # `value` is already a User instance from PrimaryKeyRelatedField
        request = self.context.get('request')
        if request and request.user and value.id == request.user.id:
            raise serializers.ValidationError("You cannot send a message to yourself.")
        return value
    
    def validate_reply_to(self, value):
        """Validate reply_to message exists if provided."""
        if value is None:
            return None
        
        try:
            reply_message = CommunicationMessage.objects.get(id=value)
            return reply_message
        except CommunicationMessage.DoesNotExist:
            raise serializers.ValidationError("Reply-to message does not exist.")

    def validate(self, data):
        """ Validate the entire message data.
        - Ensure the thread exists and is active.
        - Ensure the recipient has access to the order.
        """
        thread = self.context.get('thread')
        if not thread:
            raise serializers.ValidationError("Thread is required.")
        
        if not thread.is_active and not thread.admin_override:
            raise serializers.ValidationError("Thread is no longer active.")
        
        request = self.context.get("request")
        if data.get("message_type") == MessageType.SYSTEM:
            raise serializers.ValidationError(
                "System messages cannot be created manually."
            )
        
        # Validate recipient has access to the thread/order
        recipient = data.get('recipient')
        if recipient:
            # For threads with orders, check order access
            if thread.order:
                order = thread.order
                role = getattr(recipient, "role", None)
                has_access = (
                    order.client == recipient or
                    order.assigned_writer == recipient or
                    role in {"admin", "superadmin", "editor", "support"} or
                    recipient in thread.participants.all()
                )
                if not has_access:
                    raise serializers.ValidationError({
                        "recipient": "Selected recipient does not have access to this order."
                    })
            else:
                # For threads without orders, check if recipient is a participant
                if recipient not in thread.participants.all():
                    raise serializers.ValidationError({
                        "recipient": "Recipient is not a participant in this thread."
                    })
        
        # Validate reply_to belongs to the thread
        reply_to = data.get('reply_to')
        if reply_to and reply_to.thread != thread:
            raise serializers.ValidationError({
                "reply_to": "Reply-to message does not belong to this thread."
            })
        
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
    word = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        trim_whitespace=True
    )
    
    class Meta:
        model = ScreenedWord
        fields = ["id", "word"]
        read_only_fields = ["id"]
    
    def validate_word(self, value):
        """Validate and normalize the word."""
        if not value or not value.strip():
            raise serializers.ValidationError("Word cannot be empty.")
        # Normalize to lowercase and strip whitespace
        word = value.strip().lower()
        if len(word) > 100:
            raise serializers.ValidationError("Word cannot exceed 100 characters.")
        return word

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
    class Meta:
        model = FlaggedMessage
        fields = [
            "id",
            "order_id",
            "sender_username",
            "sanitized_message",
            "flagged_reason",
            "flagged_at",
            "admin_comment",
            "reviewed_by",
            "reviewed_at",
            "is_unblocked",
        ]
        read_only_fields = [
            "id",
            "order_id",
            "sender_username",
            "sanitized_message",
            "flagged_at",
            "reviewed_by",
            "reviewed_at",
        ]

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

class OrderMessageNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicationNotification
        fields = ["id", "order", "is_read"]

class WebSocketAuditLogSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    thread_id = serializers.CharField(source="thread.id", read_only=True)

    class Meta:
        model = WebSocketAuditLog
        fields = [
            "id", "user", "thread_id", "action", "payload", "created_at"
        ]
        read_only_fields = fields