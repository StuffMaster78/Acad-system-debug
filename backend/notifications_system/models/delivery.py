from django.db import models
from django.conf import settings
from django.utils import timezone
from notifications_system.enums import (
    NotificationChannel,
    NotificationPriority,
    DeliveryStatus,
)


class Delivery(models.Model):
    """
    Represents a single notification send attempt.
    Drives retry logic, dead-letter queue, and delivery metrics.
    One row per send attempt per channel per user.
    """
    event_key = models.CharField(max_length=128)

    website = models.ForeignKey(
        'websites.Website',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='notification_deliveries',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='notification_deliveries',
    )

    # FK to the notification this delivery belongs to
    notification = models.ForeignKey(
        'notifications_system.Notification',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='deliveries',
    )

    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
        db_index=True,
    )
    priority = models.CharField(
        max_length=16,
        choices=NotificationPriority.choices,
    )
    status = models.CharField(
        max_length=16,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.QUEUED,
    )

    # Retry tracking
    attempts = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    next_retry_at = models.DateTimeField(null=True, blank=True)

    # Provider details
    provider = models.CharField(max_length=64, blank=True)
    provider_msg_id = models.CharField(max_length=128, blank=True)

    # Failure details
    error_code = models.CharField(max_length=64, blank=True)
    error_detail = models.TextField(blank=True)

    # payload = raw input context passed to renderer
    # rendered = final output after template rendering
    payload = models.JSONField(default=dict, blank=True)
    rendered = models.JSONField(default=dict, blank=True)

    # Acknowledgement — for in-app notifications
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    # Fallback tracking
    triggered_by_fallback = models.BooleanField(
        default=False,
        help_text="True if this delivery was triggered as a fallback from another channel.",
    )

    # Deduplication
    dedupe_key = models.CharField(
        max_length=256,
        blank=True,
        unique=True,
        help_text="Prevents duplicate delivery of the same notification.",
    )

    # Timestamps
    queued_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notif_delivery'
        ordering = ['-queued_at']
        indexes = [
            models.Index(fields=['status', 'channel']),
            models.Index(fields=['user', 'website']),
            models.Index(fields=['event_key']),
            models.Index(fields=['status', 'next_retry_at']),
            models.Index(fields=['notification', 'channel']),
        ]

    def __str__(self):
        return f"{self.event_key} → {self.user} via {self.channel} [{self.status}]"

    @property
    def is_successful(self):
        return self.status == DeliveryStatus.SENT

    @property
    def has_retries_remaining(self):
        return self.attempts < self.max_retries

    @property
    def is_terminal(self):
        return self.status in (
            DeliveryStatus.SENT,
            DeliveryStatus.FAILED,
            DeliveryStatus.CANCELLED,
        )

    def record_attempt(self, success, provider_msg_id='', error_code='', error_detail=''):
        """Record the result of a delivery attempt and update retry state."""
        self.attempts += 1
        self.provider_msg_id = provider_msg_id

        if success:
            self.status = DeliveryStatus.SENT
            self.sent_at = timezone.now()
            self.next_retry_at = None
        else:
            self.error_code = error_code
            self.error_detail = error_detail
            if self.has_retries_remaining:
                self.status = DeliveryStatus.RETRY
                backoff_minutes = 2 ** self.attempts
                self.next_retry_at = timezone.now() + timezone.timedelta(
                    minutes=backoff_minutes
                )
            else:
                self.status = DeliveryStatus.FAILED
                self.next_retry_at = None

        self.save(update_fields=[
            'attempts', 'status', 'sent_at', 'next_retry_at',
            'provider_msg_id', 'error_code', 'error_detail', 'updated_at',
        ])

    def acknowledge(self):
        """Mark delivery as acknowledged by the user."""
        if not self.is_acknowledged:
            self.is_acknowledged = True
            self.acknowledged_at = timezone.now()
            self.save(update_fields=['is_acknowledged', 'acknowledged_at', 'updated_at'])