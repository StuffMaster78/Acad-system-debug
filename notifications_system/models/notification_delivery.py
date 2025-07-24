from datetime import timezone
from django.db import models
from websites.models import Website
from notifications_system.enums import (
    NotificationType,
    DeliveryStatus,
)
from notifications_system.models.notifications import Notification


class NotificationDelivery(models.Model):
    """ 
    Represents a delivery attempt for a notification.
    """
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notification_deliveries"
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="notification_deliveries"
    )
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="deliveries"
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
    )
    success = models.BooleanField(
        default=False,
        help_text="Was the delivery successful?"
    )
    status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices
    )
    response = models.TextField(
        null=True, blank=True
    )  # Optional: delivery response or error msg
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    attempted_at = models.DateTimeField(auto_now_add=True)
    triggered_by_fallback = models.BooleanField(default=False)
    sent_at = models.DateTimeField(
        null=True, blank=True
    )
    retry_count = models.IntegerField(
        default=0,
        help_text="Number of retries attempted for this delivery."
    )
    error_message = models.TextField(
        blank=True, null=True
    )

    class Meta:
        ordering = ['-attempted_at']
        unique_together = ('user', 'website', 'notification', 'channel')
        indexes = [
            models.Index(fields=['user', 'website', 'notification']),
        ]
        verbose_name = 'Notification Delivery'
        verbose_name_plural = 'Notification Deliveries'

    def __str__(self):
        return f"Delivery of {self.notification.title} via {self.channel} - Status: {self.status}"