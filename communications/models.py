import re
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from orders.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

class CommRole(models.TextChoices):
    CLIENT = "client", "Client"
    WRITER = "writer", "Writer"
    ADMIN = "admin", "Admin"
    SUPPORT = "support", "Support"
    EDITOR = "editor", "Editor"
    SUPERADMIN = "superadmin", "Super Admin"

class MessageType(models.TextChoices):
    TEXT = "text", "Text"
    FILE = "file", "File Attachment"
    LINK = "link", "Link"
    IMAGE = "image", "Image"
    SYSTEM = "system", "System Message"
    VIDEO = "video", "Video"
    AUDIO = "audio", "Audio"
    NOTE = "note", "Internal Note"
    OTHER = "other", "Other"


class ScreenedWord(models.Model):
    """
    Stores words and patterns that should be blocked in messages.
    Admins can add/remove words dynamically.
    """
    word = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.word


class CommunicationThread(models.Model):
    """
    Represents a conversation thread related to an order.
    Messaging is disabled once an order is approved and
    archived unless overridden by admin.
    """
    THREAD_TYPE_CHOICES = [
        ("client_writer", "Client ↔ Writer"),
        ("order", "Order"),
        ("internal", "Internal"),
        ("special", "Special Order"),
        ("dispute", "Dispute"),
        ("general", "General Inquiry"),
        ("revision", "Revision Request"),
        ("feedback", "Feedback"),
        ("clarification", "Clarification"),
        ("complaint", "Complaint"),
        ("request", "Request"),
        ("escalation", "Escalation"),
        ("announcement", "Announcement"),
        ("class_bundle", "Class Bundle"),
        ("support", "Support"),
        ("account", "Account"),
        ("custom", "Custom"),
        ("other", "Other"),
    ]
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="message_threads",
        help_text="Website associated with this order thread."
    )
    thread_type = models.CharField(
        max_length=20, choices=THREAD_TYPE_CHOICES,
        default="client_writer"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="message_thread"
    )
    special_order = models.ForeignKey(
        'special_orders.SpecialOrder',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="message_threads"
    )
    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    sender_role = models.CharField(max_length=50, choices=CommRole.choices)
    recipient_role = models.CharField(max_length=50, choices=CommRole.choices)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="message_threads",
        help_text="Users involved in this thread."
    )
    notifications_enabled = models.BooleanField(default=True)
    # Mute functionality to prevent notifications
    mute = models.BooleanField(
        default=False,
        help_text="Mute notifications for this thread."
    )
    # Mute until a specific time, if set
    # This allows for temporary muting of notifications
    # Useful for users who want to take a break from notifications
    # without permanently disabling them 
    # e.g., during a vacation or busy period
    # If set, notifications will not be sent until this time
    # If null, notifications are not muted
    mute_until = models.DateTimeField(null=True, blank=True)

    # Messaging is active unless order is archived
    is_active = models.BooleanField(default=True)
    # Admin can enable messaging for archived orders
    admin_override = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Whether users are allowed to send messages in this thread
    allow_messaging = models.BooleanField(default=True)

    def disable_messaging(self):
        """Disable messaging unless overridden by admin."""
        if not self.admin_override:
            self.is_active = False
            self.save()

    def enable_messaging(self):
        """Enable messaging (Admin Override)."""
        self.admin_override = True
        self.is_active = True
        self.save()

    def clean(self):
        """Ensure correct thread type association."""
        if self.thread_type == "special" and not self.special_order:
            raise ValidationError(
                "Special Order threads require a Special Order."
            )
        if self.thread_type != "special" and not self.order:
            raise ValidationError(
                "Standard threads must have an associated Order."
            )
        if self.thread_type not in dict(self.THREAD_TYPE_CHOICES):
            raise ValidationError(
                f"Invalid thread_type: {self.thread_type}"
            )

    def __str__(self):
        """
        Returns a string representation of the thread.
        """
        if self.thread_type == "special" and self.special_order:
            return f"Special Order #{self.special_order.id} Thread"
        if self.order:
            return f"Standard Order #{self.order.id} Thread"
        return f"Thread #{self.id}"
class CommunicationMessage(models.Model):
    """
    Represents a single message in an order conversation.
    Messages with flagged words will be automatically
    sanitized and flagged for admin review.
    """
    
    thread = models.ForeignKey(
        CommunicationThread, on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )
    sender_role = models.CharField(max_length=10, choices=CommRole.choices)
    message = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default="text"
    )
    is_internal_note = models.BooleanField(default=False)
    attachment = models.FileField(
        upload_to="message_attachments/",
        null=True, blank=True
    )
    contains_link = models.BooleanField(default=False)
    is_link_approved = models.BooleanField(default=False)
    link_url = models.URLField(null=True, blank=True)
    link_domain = models.CharField(max_length=255, null=True, blank=True)
    link_preview_text = models.TextField(null=True, blank=True)
    preview_failed_at = models.DateTimeField(null=True, blank=True)
    link_preview_json = models.JSONField(null=True, blank=True)

    is_hidden = models.BooleanField(
        default=False,
        help_text="Message disabled by admin or system."
        )
    is_archived = models.BooleanField(
        default=False,
        help_text="Message archived by user or admin."
    )

    created_by_admin = models.BooleanField(default=False)
    visible_to_roles = models.JSONField(
        default=list,
        help_text="List of roles allowed to see this message."
    )

    reply_to = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="replies"
    )
    read_by = models.ManyToManyField(
        User,
        through="MessageReadReceipt",
        related_name="read_messages", 
        blank=True
    )

    # Timestamps for message tracking
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    is_system = models.BooleanField(default=False)
    system_type = models.CharField(
        max_length=50, blank=True, null=True
    )

    # Soft delete functionality
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    deleted_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    is_flagged = models.BooleanField(default=False)
    is_unblocked = models.BooleanField(default=False)
    class Meta:
        ordering = ["-sent_at"]
        unique_together = ['visible_to_roles', 'is_deleted']

    def save(self, *args, **kwargs):
        """
        Override save method to sanitize message and flag if necessary.
        """
        self._sanitize_and_flag_message()
        super().save(*args, **kwargs)


    def _sanitize_and_flag_message(self):
        """
        Replaces banned content with '*****' and flags message.
        Also scans for phone numbers and emails.
        """
        banned_words = ScreenedWord.objects.values_list("word", flat=True)
        flagged = False

        for word in banned_words:
            if word.lower() in self.message.lower():
                self.message = re.sub(
                    rf"(?i)\b{re.escape(word)}\b",
                    "*****",
                    self.message,
                    flags=re.IGNORECASE
                )
                flagged = True

        phone_regex = r"\+?\d[\d -]{8,14}\d"
        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        if re.search(phone_regex, self.message) or re.search(email_regex, self.message):
            self.message = re.sub(phone_regex, "*****", self.message)
            self.message = re.sub(email_regex, "*****", self.message)
            flagged = True

        if flagged:
            FlaggedMessage.objects.create(
                message=self,
                flagged_reason="Contains restricted content"
            )

    def enforce_visibility_rules(self):
        """Sets message visibility based on sender/recipient roles."""
        admin_roles = ["admin", "superadmin", "support"]

        if self.sender_role in admin_roles:
            if self.recipient_role == "client":
                self.visible_to_writer = False
            elif self.recipient_role == "writer":
                self.visible_to_client = False
        elif self.sender_role == "client":
            self.visible_to_writer = True
            self.visible_to_client = True
        elif self.sender_role == "writer":
            self.visible_to_writer = True
            self.visible_to_client = True

    def soft_delete_message(message, user):
        """
        Soft delete a message by marking it as deleted.
        This allows for recovery if needed.
        Args:
            message (CommunicationMessage): The message to delete.
            user (User): The user performing the deletion.
        """
        message.is_deleted = True
        message.deleted_by = user
        message.deleted_at = timezone.now()
        message.save()


    def __str__(self):
        try:
            return (
                f"{self.sender_role} ({self.sender}) | Order {self.thread.order.id}"
            )
        except AttributeError:
            return f"{self.sender_role} ({self.sender}) | Thread {self.thread.id}"



class MessageReadReceipt(models.Model):
    """ Tracks read receipts for messages,
    ensuring accountability on who has viewed messages.
    This model is used to track when a user has read a message,
    allowing for better communication flow and accountability.
    """
    message = models.ForeignKey("CommunicationMessage", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("message", "user")


class CommunicationLog(models.Model):
    """
    Logs all message-related actions for tracking and auditing.
    """
    ACTION_CHOICES = [
        ("sent", "Message Sent"),
        ("read", "Message Read"),
        ("deleted", "Message Deleted"),
        ("disabled_thread", "Messaging Disabled for Order"),
        ("enabled_thread", "Messaging Enabled by Admin"),
        ("flagged", "Message Flagged for Review"),
        ("unblocked", "Message Unblocked by Admin"),
        ("resolved_dispute", "Dispute Resolved"),
        ("escalated_dispute", "Dispute Escalated"),
        ("created_thread", "Thread Created"),
        ("updated_thread", "Thread Updated"),
        ("deleted_thread", "Thread Deleted"),
        ("notification_sent", "Notification Sent"),
        ("read_receipt", "Read Receipt Created"),
        ("notification_created", "Notification Created"),
        ("other", "Other"),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="message_logs"
    )
    special_order = models.ForeignKey(
        'special_orders.SpecialOrder', on_delete=models.CASCADE,
        null=True, blank=True, related_name="message_logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)  # Optional extra info

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user} - {self.action} in Order {self.order.id} at {self.timestamp}"


class FlaggedMessage(models.Model):
    """
    Stores messages flagged for review.
    Admins can review and either unblock or confirm the flag.
    """
    message = models.OneToOneField(
        CommunicationMessage, on_delete=models.CASCADE,
        related_name="flagged_message"
    )
    flagged_reason = models.TextField()
    flagged_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_comment = models.TextField(blank=True, null=True)
    is_unblocked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-flagged_at"]

    def __str__(self):
        return f"Flagged Message (Order {self.message.thread.order.id})"

    def unblock(self, admin_user, comment=""):
        """Admin manually unblocks a flagged message with a comment."""
        self.is_unblocked = True
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.admin_comment = comment
        self.save()

    def send_flagged_notification(self):
        """Email all staff users about a flagged message."""
        admins = User.objects.filter(is_staff=True)
        emails = [a.email for a in admins if a.email]

        if emails:
            send_mail(
                subject="Flagged Message Alert",
                message=(
                    f"Order {self.message.thread.order.id} was flagged.\n"
                    f"Message: {self.message.message}\n"
                    f"Sender: {self.message.sender.username}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails
            )


class CommunicationReadReceipt(models.Model):
    """
    Tracks read receipts for messages, ensuring
    accountability on who has viewed messages.
    """
    message = models.ForeignKey(
        CommunicationMessage,
        on_delete=models.CASCADE,
        related_name="read_receipts"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")

    def __str__(self):
        return f"Read by {self.user} at {self.read_at}"



class CommunicationNotification(models.Model):
    """
    Stores notifications for unread messages and flagged messages.
    If a message is flagged, an admin gets notified.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_notifications",
        null=True, blank=True
    )
    message = models.ForeignKey(
        "CommunicationMessage",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True, blank=True
    )
    notification_text = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        """
        Set auto-expiration for flagged message notifications.
        """
        is_flagged_text = (
            self.notification_text and
            "flagged" in self.notification_text.lower()
        )
        if is_flagged_text and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        mid = self.message.id if self.message else "Flagged"
        return f"Notification for {self.recipient} - Message {mid}"

    # def __str__(self):
    #     return (
    #         f"Notification for {self.recipient} - "
    #         f" Message {self.message.id if self.message else 'Flagged Message'}"
    #     )



class DisputeMessage(models.Model):
    """
    Represents a message in the dispute process
    between clients, writers, and admins.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("escalated", "Escalated"),
    ]
    
    CATEGORY_CHOICES = [
        ("clarification", "Clarification"),
        ("complaint", "Complaint"),
        ("request", "Request"),
        ("feedback", "Feedback"),
        ("other", "Other"),
    ]

    message = models.OneToOneField(
        CommunicationMessage, on_delete=models.CASCADE,
        related_name="dispute_message"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    sender_role = models.CharField(
        max_length=10, choices=CommRole.choices
    )
    content = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="other"
    )
    resolution_comment = models.TextField(blank=True, null=True)
    resolution_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="dispute_resolution"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return (
                f"Dispute (Order {self.message.thread.order.id}) - "
                f"{self.get_status_display()}"
            )

    def resolve(self, admin_user, resolution_comment=""):
        """
        Resolve the dispute with an optional comment.

        Args:
            admin_user (User): The admin resolving the dispute.
            resolution_comment (str, optional): Details on the resolution.
        """
        self.status = "resolved"
        self.resolution_comment = resolution_comment
        self.resolution_by = admin_user
        self.resolved_at = timezone.now()
        self.save()


class WebSocketAuditLog(models.Model):
    """
    Represents a log of WebSocket actions
    for auditing purposes. This is useful for tracking
    user interactions with WebSocket connections,
    such as message sending, thread creation, and more.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    thread = models.ForeignKey(
        "CommunicationThread",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    action = models.CharField(max_length=50)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

class SystemAlert(models.Model):
    """
    Represents system-generated alerts for admins.
    These can be triggered by various events such as
    flagged messages, disputes, or other significant actions.
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    category = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_alerts'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    acknowledged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']