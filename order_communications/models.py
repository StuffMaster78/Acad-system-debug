import re
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from orders.models import Order

class ScreenedWord(models.Model):
    """
    Stores words and patterns that should be blocked in messages.
    Admins can add/remove words dynamically.
    """
    word = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.word


class OrderMessageThread(models.Model):
    """
    Represents a conversation thread related to an order.
    Messaging is disabled once an order is approved and archived unless overridden by admin.
    """
    ORDER_TYPE_CHOICES = [
        ('standard', 'Standard Order'),
        ('special', 'Special Order'),
    ]
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='standard', help_text="Type of order this thread is associated with.")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="message_thread")
    special_order = models.ForeignKey('special_orders.SpecialOrder', on_delete=models.CASCADE, null=True, blank=True, related_name="message_threads")

    sender_role = models.CharField(max_length=50, choices=[
        ('writer', 'Writer'), 
        ('client', 'Client'), 
        ('admin', 'Admin'),
        ('editor', 'Editor'), 
        ('support', 'Support')
    ])
    recipient_role = models.CharField(max_length=50, choices=[
        ('writer', 'Writer'), 
        ('client', 'Client'), 
        ('admin', 'Admin'),
        ('editor', 'Editor'),  
        ('support', 'Support')
    ])
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="message_threads", help_text="Users involved in this thread.")
    is_active = models.BooleanField(default=True)  # Messaging is active unless order is archived
    admin_override = models.BooleanField(default=False)  # Admin can enable messaging for archived orders
    created_at = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        if self.order_type == "special":
            return f"Special Order #{self.special_order.id} Thread"
        return f"Standard Order #{self.order.id} Thread"


class OrderMessage(models.Model):
    """
    Represents a single message in an order conversation.
    Messages with flagged words will be automatically sanitized and flagged for admin review.
    """
    ROLE_CHOICES = [
        ("client", "Client"),
        ("writer", "Writer"),
        ("admin", "Admin"),
        ("support", "Support"),
        ("editor", "Editor"),
    ]

    thread = models.ForeignKey(OrderMessageThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sender_role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Soft delete functionality
    is_flagged = models.BooleanField(default=False)
    is_unblocked = models.BooleanField(default=False)
    class Meta:
        ordering = ["-sent_at"]

    def clean(self):
        """Sanitize message before saving and flag it if necessary."""
        self._sanitize_and_flag_message()

    def _sanitize_and_flag_message(self):
        """
        Replaces banned words with '*****' and flags the message for admin review.
        """
        banned_words = ScreenedWord.objects.values_list("word", flat=True)
        flagged = False

        # Sanitize message
        for word in banned_words:
            if word.lower() in self.message.lower():
                self.message = re.sub(rf"\b{word}\b", "*****", self.message, flags=re.IGNORECASE)
                flagged = True

        # Check for phone numbers and emails
        PHONE_REGEX = r"\+?\d[\d -]{8,14}\d"
        EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        if re.search(PHONE_REGEX, self.message) or re.search(EMAIL_REGEX, self.message):
            self.message = re.sub(PHONE_REGEX, "*****", self.message)
            self.message = re.sub(EMAIL_REGEX, "*****", self.message)
            flagged = True

        if flagged:
            FlaggedMessage.objects.create(order_message=self, flagged_reason="Contains restricted content")

    def __str__(self):
        return f"{self.sender_role} ({self.sender}) in Order {self.thread.order.id}"


class OrderMessageLog(models.Model):
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
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="message_logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
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
    order_message = models.OneToOneField(OrderMessage, on_delete=models.CASCADE, related_name="flagged_message")
    flagged_reason = models.TextField()
    flagged_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_comment = models.TextField(blank=True, null=True)
    is_unblocked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-flagged_at"]

    def __str__(self):
        return f"Flagged Message (Order {self.order_message.thread.order.id})"

    def unblock(self, admin_user, comment=""):
        """Admin manually unblocks a flagged message with a comment."""
        self.is_unblocked = True
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.admin_comment = comment
        self.save()

    def send_flagged_notification(self):
        """Send email notification to admins about the flagged message."""
        admin_users = get_user_model().objects.filter(is_staff=True)
        admin_emails = [admin.email for admin in admin_users if admin.email]

        if admin_emails:
            send_mail(
                subject="Flagged Message Alert",
                message=f"A message in Order {self.order_message.thread.order.id} has been flagged.\n\n"
                        f"Message: {self.order_message.message}\n"
                        f"Sender: {self.order_message.sender.username}\n\n"
                        f"Please review it in the admin portal.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
            )


class OrderMessageReadReceipt(models.Model):
    """
    Tracks read receipts for messages, ensuring accountability on who has viewed messages.
    """
    message = models.ForeignKey(OrderMessage, on_delete=models.CASCADE, related_name="read_receipts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("message", "user")  # Prevent duplicate read receipts

    def __str__(self):
        return f"Read by {self.user} at {self.read_at}"



class OrderMessageNotification(models.Model):
    """
    Stores notifications for unread messages and flagged messages.
    If a message is flagged, an admin gets notified.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order_notifications", null=True, blank=True
    )
    message = models.ForeignKey(
        "OrderMessage", on_delete=models.CASCADE, related_name="notifications", null=True, blank=True
    )
    notification_text = models.TextField(null=True, blank=True)  # For flagged messages
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Expiration time for flagged notifications

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        """Automatically set expiration for flagged message notifications."""
        if "flagged" in self.notification_text.lower() and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)  # Auto-expire flagged notifications in 7 days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Notification for {self.recipient} - Message {self.message.id if self.message else 'Flagged Message'}"



class DisputeMessage(models.Model):
    """
    Represents a message in the dispute process between clients, writers, and admins.
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

    order_message = models.OneToOneField(OrderMessage, on_delete=models.CASCADE, related_name="dispute_message")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sender_role = models.CharField(max_length=10, choices=OrderMessage.ROLE_CHOICES)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    resolution_comment = models.TextField(blank=True, null=True)
    resolution_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="dispute_resolution")
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispute Message (Order {self.order_message.thread.order.id}) - {self.get_status_display()}"

    def resolve(self, admin_user, resolution_comment=""):
        """Resolve the dispute message."""
        self.status = "resolved"
        self.resolution_comment = resolution_comment
        self.resolution_by = admin_user
        self.resolved_at = timezone.now()
        self.save()