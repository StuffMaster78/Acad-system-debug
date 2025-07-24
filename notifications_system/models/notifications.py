from datetime import timezone
from django.db import models
from django.utils.timezone import now
from core.models.base import WebsiteSpecificBaseModel
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
from notifications_system.models.notification_log import NotificationLog


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
    priority_label = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Label for the priority, e.g. 'high', 'medium', 'low'"
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
    is_broadcast = models.BooleanField(default=False)
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
    delivered = models.BooleanField(
        default=False,
        help_text="Has the notification been delivered?"
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
    failed_channels = models.JSONField(default=list)  # e.g., ["email", "push"]
    metadata = models.JSONField(
        default=dict,
        blank=True
    )  # optional for payload debugging
    pinned = models.BooleanField(
        default=False,
        help_text="Whether the notification is pinned."
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the notification expires and shouldn't be shown."
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
            models.Index(fields=['is_digest', 'digest_group']),
            models.Index(fields=['priority']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type.capitalize()} Notification to {self.user.username}: {self.title}"