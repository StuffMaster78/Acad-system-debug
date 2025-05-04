from django.db import models
from django.utils.timezone import now
from core.models.base import WebsiteSpecificBaseModel
from users.models import User
from websites.models import Website

class Notification(models.Model):
    """
    Represents a notification sent to a user.
    """
    NOTIFICATION_TYPES = (
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('ws', 'websocket'),
        ('push', 'Push Notification'),
    )

    CATEGORY_CHOICES = (
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('announcement', 'Announcement'),
    )

    DELIVERY_STATUSES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delayed', 'Delayed'),
        ('queued', 'Queued'),
    )
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
        choices=NOTIFICATION_TYPES,
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
    is_read = models.BooleanField(
        default=False,
        help_text="Has the user read this notification?"
    )
    status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUSES,
        default='pending',
        help_text="Delivery status of the notification."
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='info',  # Set default category to 'info'
        blank=True,
        null=True,
        help_text="Category of the notification."
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification was sent."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_attempts = models.IntegerField(
        default=0,
        help_text="Number of attempts made to deliver the notification."
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

    def __str__(self):
        return f"{self.type.capitalize()} Notification to {self.user.username}: {self.title}"


class NotificationPreference(WebsiteSpecificBaseModel):
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
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('es', 'Spanish'), ('fr', 'French')],
        default='en',
        help_text="Preferred language for notifications."
    )

    def __str__(self):
        return f"Notification Preferences for {self.user.username}"


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