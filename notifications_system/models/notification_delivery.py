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