from django.db import models
from django.conf import settings
from django.utils import timezone
from notifications_system.enums import (
    NotificationChannel,
    NotificationCategory,
    NotificationPriority,
    DeliveryStatus,
)


class Notification(models.Model):
    """
    A single notification instance targeting one user.
    Immutable after creation — represents the intent to notify.

    Delivery details (attempts, retries, provider responses)
    live on related Delivery rows, not here.

    User-specific state (read, pinned, acknowledged)
    lives on NotificationsUserStatus, not here.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )

    # Who triggered this notification — null means system
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='triggered_notifications',
    )

    event_key = models.CharField(
        max_length=128,
        help_text="Event that triggered this notification e.g. 'order.completed'",
    )
    category = models.CharField(
        max_length=50,
        choices=NotificationCategory.choices,
        default=NotificationCategory.INFO,
        blank=True,
    )
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    # Channels this notification should be delivered through
    channels = models.JSONField(
        default=list,
        help_text="Channels e.g. ['email', 'in_app']",
    )

    # Raw context passed to template renderer
    payload = models.JSONField(
        default=dict,
        help_text="Context variables for template rendering.",
    )

    # Rendered output — populated after rendering
    rendered = models.JSONField(
        default=dict,
        blank=True,
        help_text="Rendered output: title, message, subject, link etc.",
    )

    # Delivery state — summary only, details are on Delivery rows
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
    )
    failed_channels = models.JSONField(
        default=list,
        blank=True,
        help_text="Channels that failed delivery e.g. ['email']",
    )

    # Behavior flags
    is_silent = models.BooleanField(
        default=False,
        help_text="Store only — do not deliver to user.",
    )
    is_critical = models.BooleanField(
        default=False,
        help_text="Bypasses user preferences and DND.",
    )
    is_broadcast = models.BooleanField(
        default=False,
        help_text="True if this was generated from a broadcast.",
    )
    is_digest = models.BooleanField(
        default=False,
        help_text="True if this should be grouped into a digest.",
    )
    digest_group = models.CharField(
        max_length=100,
        blank=True,
        help_text="Digest group key e.g. 'daily_summary'",
    )
    test_mode = models.BooleanField(
        default=False,
        help_text="If True, notification is logged but not delivered.",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="After this time the notification should not be shown.",
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'website', 'status']),
            models.Index(fields=['event_key', 'website']),
            models.Index(fields=['is_digest', 'digest_group']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['priority', 'status']),
        ]

    def __str__(self):
        return f"{self.event_key} → {self.user} [{self.status}]"

    @property
    def is_expired(self):
        return bool(self.expires_at and self.expires_at < timezone.now())

    @property
    def title(self):
        """Convenience accessor for rendered title."""
        return self.rendered.get('title', '')

    @property
    def message(self):
        """Convenience accessor for rendered message."""
        return self.rendered.get('message', '')

    @property
    def subject(self):
        """Convenience accessor for rendered email subject."""
        return self.rendered.get('subject', '')

    def mark_sent(self):
        """Mark notification as successfully sent."""
        self.status = DeliveryStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])

    def mark_failed(self, channel=None):
        """Mark notification as failed, optionally recording the failed channel."""
        if channel and channel not in self.failed_channels:
            self.failed_channels.append(channel)
        self.status = DeliveryStatus.FAILED
        self.save(update_fields=['status', 'failed_channels', 'updated_at'])