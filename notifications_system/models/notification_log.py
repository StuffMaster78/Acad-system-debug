from datetime import timezone
from django.db import models
from django.conf import settings
from websites.models import Website
from notifications_system.enums import (
    DigestType,
    NotificationType,
    NotificationCategory,
    DeliveryStatus,
    EventType,
    NotificationPriority
)
from django.contrib.postgres.fields import ArrayField
from users.mixins import UserRole   
from django.contrib.postgres.fields import JSONField
from notifications_system.models.notification_preferences import UserNotificationPreference
from notifications_system.models.notifications import Notification

User = settings.AUTH_USER_MODEL 


class NotificationLog(models.Model):
    """ Represents a log entry for a notification delivery attempt.
    """
    user =  models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_logs"
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="notification_logs"
    )
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
    event = models.CharField(
        max_length=100,
        choices=EventType.choices(),
        help_text="Event that triggered this notification."
    )
    payload = models.JSONField(
        default=dict,
        help_text="Payload sent with the notification."
    )
    delivered = models.BooleanField(default=False)
    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices(),
        default=DeliveryStatus.PENDING,
        help_text="Current delivery status of the notification."
    )
    delivery_attempts = models.IntegerField(default=0, help_text="Number of delivery attempts made.")
    priority = models.IntegerField(
        default=NotificationPriority.NORMAL,
        help_text="Priority of the notification, higher number = more urgent"
    )
    channel = models.CharField(max_length=20, choices=NotificationType.choices)
    attempted_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    response = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.notification.title} via {self.channel} - Success: {self.success}"
    

class EmailNotificationLog(models.Model):
    """ Represents a log entry for an email delivery attempt.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        "notifications.NotificationGroup",
        null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices(),
        default=DeliveryStatus.PENDING,
        help_text="Current delivery status of the email."
    )
    response_code = models.IntegerField(
        null=True, blank=True,
        help_text="HTTP response code from the email delivery attempt."
    )
    response_message = models.TextField(
        null=True, blank=True,
        help_text="Response message from the email delivery attempt."
    )