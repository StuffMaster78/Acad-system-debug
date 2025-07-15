from django.db import models
from django.utils.timezone import now
from core.models.base import WebsiteSpecificBaseModel
from django.conf import settings
from websites.models import Website
from notifications_system.notification_enums import (
    DigestType,
    NotificationType,
    NotificationCategory,
    DeliveryStatus,
    EventType,
)

User = settings.AUTH_USER_MODEL 
class Notification(models.Model):
    """
    Represents a notification sent to a user.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="system_notifications"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_notifications",
        help_text="The user receiving the notification."
    )
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default='in_app',
        help_text="The type of notification."
    )
    title = models.CharField(
        max_length=255,
        help_text="Notification title."
    )
    message = models.TextField(
        help_text="Notification content."
    )
    link = models.URLField(
        blank=True, null=True,
        help_text="Link to more information or action."
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Has the user read this notification?"
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default='pending',
        help_text="Delivery status of the notification."
    )
    category = models.CharField(
        max_length=20,
        choices=NotificationCategory.choices,
        default='info',
        blank=True,
        null=True,
        help_text="Category of the notification."
    )
    event = models.CharField(
        max_length=100,
        choices=EventType.choices,
        help_text="Event name, e.g. 'order_assigned'"
    )
    payload = models.JSONField(
        default=dict,
        help_text="Structured data for templating"
    )
    template_name = models.CharField(
        max_length=100,
        blank=True, null=True
    )
    is_silent = models.BooleanField(
        default=False,
        help_text="Do not deliver to user, only log/store"
    )
    is_critical = models.BooleanField(
        default=False,
        help_text="Is this a critical notification that requires immediate attention?"
    )
    is_digest = models.BooleanField(
        default=False,
        help_text="Should this be included in digest?"
    )
    digest_group = models.CharField(
        max_length=100,
        blank=True, null=True,
        choices=DigestType.choices,
        help_text="Group for digest notifications, e.g. 'daily_summary'"
    )
    template_version = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    priority = models.IntegerField(
        default=5,
        help_text="Higher number = more urgent"
    )
    actor = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications_triggered"
    )
    rendered_title = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Rendered title for templating"
    )
    rendered_message = models.TextField(blank=True, null=True)
    rendered_link = models.URLField(blank=True, null=True)
    rendered_context = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Rendered payload for templating"
    )
    test_mode = models.BooleanField(
        default=False,
        help_text="If true, do not deliver for real."
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification was sent."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification was delivered."
    )
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        help_text="Current delivery status of the notification."
    )
    delivery_attempts = models.IntegerField(
        default=0,
        help_text="Number of attempts made to deliver the notification."
    )
    retry_count = models.IntegerField(
        default=0,
        help_text="Number of retries attempted for this notification."
    )

    def mark_as_read(self):
        """
        Mark the notification as read.
        """
        self.is_read = True
        self.save()

    def send(self):
        """
        Simulate sending the notification. Extend this for email/SMS integrations.
        """
        self.status = 'sent'
        self.sent_at = now()
        self.delivery_attempts += 1
        self.save()

    def mark_delivered(self):
        self.delivery_status = DeliveryStatus.SENT
        self.delivered_at = now()
        self.save(update_fields=["delivery_status", "delivered_at"])

    def record_attempt(self, success, channel, response=None):
        NotificationLog.objects.create(
            notification=self,
            channel=channel,
            success=success,
            response=response
        )
        self.delivery_attempts += 1
        self.save(update_fields=["delivery_attempts"])

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        unique_together = ('website', 'user', 'type', 'title', 'message')
        indexes = [
            models.Index(fields=['website', 'user', 'type', 'is_read']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['delivered_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type.capitalize()} Notification to {self.user.username}: {self.title}"


class NotificationPreference(models.Model):
    """
    User preferences for notifications.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="system_notifications_settings"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        help_text="The user whose preferences are being managed."
    )
    event = models.CharField(
        max_length=100,
        choices=EventType.choices,
        verbose_name=("Event Type")
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        verbose_name=("Notification Channel")
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Are notifications enabled for this user?"
    )
    frequency = models.CharField(
        max_length=20,
        choices=[('immediate', 'Immediate'), ('daily', 'Daily'), ('weekly', 'Weekly')],
        default='immediate',
        help_text="Frequency of notifications."
    )
    do_not_disturb_until = models.TimeField(
        null=True,
        blank=True,
        help_text="Time until which notifications are muted."
    )
    receive_email = models.BooleanField(
        default=True,
        help_text="Allow email notifications."
    )
    receive_sms = models.BooleanField(
        default=False,
        help_text="Allow SMS notifications."
    )
    receive_push = models.BooleanField(
        default=True,
        help_text="Allow push notifications."
    )
    receive_in_app = models.BooleanField(
        default=True,
        help_text="Allow in-app notifications."
    )
    
    def __str__(self):
        return f"Notification Preferences for {self.user.username}"
    

    def get_active_channels(self):
        return [
            channel for channel, enabled in {
                NotificationType.EMAIL: self.receive_email,
                NotificationType.SMS: self.receive_sms,
                NotificationType.PUSH: self.receive_push,
                NotificationType.IN_APP: self.receive_in_app,
            }.items() if enabled
        ]



# ✅ Lazy Import to Avoid Circular Import Issues
def get_notification_model():
    from notifications_system.models import Notification
    return Notification


def send_notification(recipient, title, message, category="in_app"):
    """
    Send a notification to a user.

    :param recipient: User receiving the notification
    :param title: Notification title
    :param message: Notification content
    :param category: Type of notification (in_app, email, SMS, push)
    """
    Notification = get_notification_model()

    notification = Notification.objects.create(
        user=recipient,
        type=category,
        title=title,
        message=message,
        status="pending",
        sent_at=now(),
    )

    # Simulate sending
    notification.status = "sent"
    notification.save()
    
    return notification


class NotificationDelivery(models.Model):
    """ 
    Represents a delivery attempt for a notification.
    """
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="deliveries"
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices
    )
    sent_at = models.DateTimeField(
        null=True, blank=True
    )
    attempts = models.IntegerField(default=0)
    error_message = models.TextField(
        blank=True, null=True
    )

    def __str__(self):
        return f"Delivery of {self.notification.title} via {self.channel} - Status: {self.status}"

class NotificationLog(models.Model):
    """ Represents a log entry for a notification delivery attempt.
    """
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_logs"
    )
    response_code = models.IntegerField(
        null=True, blank=True,
        help_text="HTTP response code from the delivery attempt."
    )
    response_message = models.TextField(
        null=True, blank=True,
        help_text="Response message from the delivery attempt."
    )
    channel = models.CharField(max_length=20, choices=NotificationType.choices)
    attempted_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    response = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Log for {self.notification.title} via {self.channel} - Success: {self.success}"