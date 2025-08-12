from datetime import timezone
from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from notifications_system.enums import (
    NotificationType,
    NotificationCategory,
    DeliveryStatus
)
from django.contrib.postgres.fields import ArrayField
from users.mixins import UserRole   
from django.contrib.postgres.fields import JSONField

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class NotificationDigest(models.Model):
    """
    Represents a notification digest for a user.
    This allows notifications to be grouped into a digest for periodic delivery.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_digests"
    )
    role = models.CharField(
        max_length=50,
        choices=UserRole.choices,
        blank=True,
        null=True,
        help_text="Role of the user for this digest"
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="notification_digests"
    )
    digest_group = models.CharField(
        max_length=100,
        help_text="Group for digest notifications, e.g. 'daily_summary'"
    )
    event = models.CharField(
        max_length=100,
        help_text="Event type for the digest, e.g. 'order_updates'"
    )
    category = models.CharField(
        max_length=50,
        choices=NotificationCategory.choices,
        default=NotificationCategory.INFO,
        help_text="Category of the notification digest"
    )
    channels = ArrayField(
        models.CharField(
            max_length=50,
            choices=NotificationType.choices
        ),
        default=list,
        help_text="Channels through which the digest will be sent"
    )
    template_name = models.CharField(
        max_length=100,
        blank=True, null=True,
        help_text="Template name for rendering the digest"
    )
    priority = models.IntegerField(
        default=5,
        help_text="Higher number = more urgent"
    )
    priority_label = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )
    event_key = models.CharField(
        max_length=100,
        help_text="Key identifying the type of digest"
    )
    payload = models.JSONField(
        default=dict, help_text="Payload for the digest"
    )
    scheduled_for = models.DateTimeField(
        help_text="When the digest is scheduled to be sent"
    )

    is_sent = models.BooleanField(
        default=False, help_text="Has this digest been sent?"
    )
    is_critical = models.BooleanField(
        default=False,
        help_text="Is this a critical digest entry?"
    )
    is_read = models.BooleanField(default=False)
    
    
    rendered_title = models.CharField(
        max_length=255, blank=True, null=True
    )
    rendered_message = models.TextField(
        blank=True, null=True
    )
    rendered_link = models.URLField(
        blank=True, null=True
    )
    rendered_context = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Rendered payload for templating"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Notification Digest"
        verbose_name_plural = "Notification Digests"
        ordering = ["-scheduled_for"]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'event_key', 'scheduled_for'],
                name='unique_user_event_scheduled'
            )
        ]   
        unique_together = ('user', 'event_key', 'scheduled_for')
        indexes = [
            models.Index(fields=['user', 'event_key', 'scheduled_for']),
        ]
        permissions = [
            ("can_view_notification_digest", "Can view notification digest"),
            ("can_send_notification_digest", "Can send notification digest"),
        ]


    def __str__(self):
        return (
            f"Digest for {self.user.username} - {self.group} - {self.event} - "
            f"{self.event_key} at {self.scheduled_for}"
        )


class NotificationDigestQueue(models.Model):
    """ Represents a queue for notification digests to be sent.
    This allows digests to be processed and sent in batches.
    """
    digest = models.ForeignKey(
        NotificationDigest,
        on_delete=models.CASCADE,
        related_name="queue_entries"
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        help_text="Current status of the digest in the queue."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_key = models.CharField(max_length=255)
    payload = models.JSONField()
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        null=True, blank=True
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["event_key", "timestamp"]),
            models.Index(fields=["website", "timestamp"]),
        ]
        ordering = ["timestamp"]