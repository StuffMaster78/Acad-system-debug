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

class BroadcastNotification(models.Model):
    """
    Represents a notification that can be broadcast to multiple users.
    This is useful for system-wide or website-wide announcements or alerts.
    """
    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100, choices=EventType.choices())
    message = models.TextField()
    website = models.ForeignKey(Website, on_delete=models.CASCADE, null=True, blank=True)
    roles = models.ManyToManyField(
        UserRole, blank=True, help_text="Limit to roles (e.g. Writer, Client)"
    )
    target_roles = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    is_optional = models.BooleanField(default=False, help_text="Respects user preferences if True")
    is_active = models.BooleanField(default=True)
    channels = models.JSONField(default=list)  # ['in_app', 'email']
    show_to_all = models.BooleanField(default=False)
    scheduled_for = models.DateTimeField(null=True, blank=True)

    pinned = models.BooleanField(default=False)
    dismissible = models.BooleanField(default=True)

    send_email = models.BooleanField(default=False)
    show_in_dashboard = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-pinned', '-created_at']

    def __str__(self):
        return self.title
    

class BroadcastOverride(models.Model):
    """
    Represents an override for a broadcast notification.
    This allows specific users or roles to receive or ignore a broadcast notification.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="broadcast_overrides"
    )
    broadcast = models.ForeignKey(
        BroadcastNotification,
        on_delete=models.CASCADE,
        related_name="overrides"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="broadcast_overrides"
    )
    role = models.ForeignKey(
        UserRole,
        on_delete=models.CASCADE,
        related_name="broadcast_overrides"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    event_type = models.CharField(max_length=100, choices=EventType.choices())
    force_channels = ArrayField(models.CharField(max_length=50, choices=NotificationType.choices()))
    title = models.CharField(max_length=255)
    message = models.TextField()


    def __str__(self):
        return super().__str__()
    
    class Meta:
        db_table = ''
        managed = True
        verbose_name = 'Broadcast Override'
        verbose_name_plural = 'Broadcast Overrides'
        indexes = [
            models.Index(fields=['website', 'broadcast', 'user', 'role']),
        ]
