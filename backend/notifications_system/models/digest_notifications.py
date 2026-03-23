from django.db import models
from django.conf import settings
from django.utils import timezone
from websites.models.websites import Website
from notifications_system.enums import (
    NotificationCategory,
    NotificationPriority,
    DeliveryStatus,
)


class NotificationDigest(models.Model):
    """
    Groups multiple notifications into a single periodic delivery.
    e.g. a daily summary email of all order updates.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_digests',
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='notification_digests',
    )

    digest_group = models.CharField(
        max_length=100,
        help_text="Grouping key e.g. 'daily_summary', 'weekly_report'",
    )
    event = models.CharField(
        max_length=100,
        help_text="Event type e.g. 'order_updates'",
    )
    event_key = models.CharField(
        max_length=100,
        help_text="Unique identifier for this digest type",
    )
    category = models.CharField(
        max_length=50,
        choices=NotificationCategory.choices,
        default=NotificationCategory.INFO,
    )
    channels = models.JSONField(
        default=list,
        help_text="Delivery channels e.g. ['email', 'in_app']",
    )
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )
    template_name = models.CharField(max_length=100, blank=True)

    # Raw context passed to the template renderer
    payload = models.JSONField(default=dict)

    # Rendered output — populated after rendering, before sending
    rendered = models.JSONField(
        default=dict,
        blank=True,
        help_text="Rendered output: title, message, link, context",
    )

    # State
    is_sent = models.BooleanField(default=False)
    is_critical = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    # Scheduling
    scheduled_for = models.DateTimeField(
        help_text="When this digest is scheduled to be sent",
    )
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Digest'
        verbose_name_plural = 'Notification Digests'
        ordering = ['-scheduled_for']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'event_key', 'scheduled_for'],
                name='unique_user_event_scheduled',
            )
        ]
        indexes = [
            models.Index(fields=['user', 'website', 'is_sent']),
            models.Index(fields=['scheduled_for', 'is_sent']),
            models.Index(fields=['user', 'event_key', 'scheduled_for']),
        ]
        permissions = [
            ('can_view_notification_digest', 'Can view notification digest'),
            ('can_send_notification_digest', 'Can send notification digest'),
        ]

    def __str__(self):
        return (
            f"Digest for {self.user} — {self.digest_group} "
            f"— {self.event_key} at {self.scheduled_for}"
        )

    def mark_sent(self):
        """Mark digest as sent."""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save(update_fields=['is_sent', 'sent_at', 'updated_at'])

    def mark_read(self):
        """Mark digest as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read', 'updated_at'])


class NotificationDigestQueue(models.Model):
    """
    Queue entry for a digest pending processing.
    Tracks delivery status only — all content is on the digest itself.
    """
    digest = models.ForeignKey(
        NotificationDigest,
        on_delete=models.CASCADE,
        related_name='queue_entries',
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
    )
    error_detail = models.TextField(blank=True)
    attempts = models.PositiveIntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['digest', 'status']),
        ]

    def __str__(self):
        return f"Queue entry for digest {self.digest.pk} [{self.status}]"