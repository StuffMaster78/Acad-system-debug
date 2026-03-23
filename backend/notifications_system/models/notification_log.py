from django.db import models
from django.conf import settings
from notifications_system.enums import (
    NotificationChannel,
    DeliveryStatus,
    NotificationPriority,
)


class NotificationLog(models.Model):
    """
    Immutable audit log of every notification delivery attempt.
    Never updated after creation — one row per attempt.
    Separate from Delivery which is the operational retry table.

    Use this for: audit trails, analytics, support investigations.
    Use Delivery for: retry logic, queue management, deduplication.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_logs',
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='notification_logs',
    )
    notification = models.ForeignKey(
        'notifications_system.Notification',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
    )
    delivery = models.ForeignKey(
        'notifications_system.Delivery',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
        help_text="The delivery attempt this log entry corresponds to.",
    )
    group = models.ForeignKey(
        'notifications_system.NotificationGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notification_logs',
    )

    event_key = models.CharField(max_length=128)
    channel = models.CharField(
        max_length=20,
        choices=NotificationChannel.choices,
    )
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
    )

    # Provider response
    response_code = models.IntegerField(null=True, blank=True)
    response_message = models.TextField(blank=True)

    # Failure detail
    error_code = models.CharField(max_length=64, blank=True)
    error_detail = models.TextField(blank=True)

    # Email-specific fields — null for non-email channels
    email_subject = models.CharField(max_length=255, blank=True)
    email_body = models.TextField(blank=True)

    # Context snapshot at time of send — useful for debugging
    payload = models.JSONField(default=dict, blank=True)

    attempt_number = models.PositiveIntegerField(
        default=1,
        help_text="Which attempt this log entry represents.",
    )
    is_successful = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['user', 'website', 'status']),
            models.Index(fields=['event_key', 'channel']),
            models.Index(fields=['notification', 'channel']),
            models.Index(fields=['attempted_at']),
        ]

    def __str__(self):
        return (
            f"{self.event_key} → {self.user} via {self.channel} "
            f"[{self.status}] at {self.attempted_at}"
        )