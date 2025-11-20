from datetime import timezone
from django.db import models

from django.conf import settings
import users
from websites.models import Website
from notifications_system.enums import (
    NotificationPriority
)
from notifications_system.models.notifications import Notification
from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

class NotificationsUserStatus(models.Model):
    """
    Represents the status of a user regarding notifications.
    This model tracks whether a user has acknowledged
    or read a notification, pinning, 
    priorities, and read statuses for notifications
    per user or per notification copy,
    as well as their preferences for receiving future notifications.
    """ 
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="notification_statuses"
    )
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="user_statuses"
    )
    is_acknowledged = models.BooleanField(default=False)
    is_acknowledged_at = models.DateTimeField(null=True, blank=True)

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)
    
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices(),
        default=NotificationPriority.NORMAL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'notification')
        verbose_name = 'User Notification Status'
        verbose_name_plural = 'User Notification Statuses'
    indexes = [
        models.Index(fields=['user', 'notification']),
        models.Index(fields=['user', 'is_acknowledged']),
        models.Index(fields=['user', 'is_read']),
        models.Index(fields=['notification', 'priority']),
    ]

    def __str__(self):
        return f"{self.user.username} - {self.notification.title} Status"