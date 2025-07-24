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
    event_type = models.CharField(
        max_length=100, choices=EventType.choices()
    )
    message = models.TextField()

    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        null=True, blank=True
    )
    show_to_all = models.BooleanField(default=False)
    target_roles = ArrayField(models.CharField(
        max_length=50), default=list, blank=True
    )

    channels = models.JSONField(default=list)  # ['in_app', 'email']

    is_optional = models.BooleanField(
        default=False,
        help_text="Respects user preferences if True"
    )
    is_blocking = models.BooleanField(default=True)
    require_acknowledgement = models.BooleanField(default=True)

    pinned = models.BooleanField(default=False)
    dismissible = models.BooleanField(default=True)
    send_email = models.BooleanField(default=False)
    show_in_dashboard = models.BooleanField(default=True)
    
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
  
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True
    )
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        ordering = ['-pinned', '-created_at']
        verbose_name = 'Broadcast Notification'
        verbose_name_plural = 'Broadcast Notifications'
        indexes = [
            models.Index(fields=['website', 'event_type']),
            models.Index(fields=['-created_at']),
        ]
        unique_together = ('website', 'title', 'event_type')
        db_table = 'broadcast_notification'

    def __str__(self):
        return f"[{self.website}] {self.title}"
    
    @property
    def is_expired(self):
        return self.expires_at and self.expires_at < timezone.now()

class BroadcastAcknowledgement(models.Model):
    """
    Represents a user's acknowledgement of a broadcast notification.
    This is used to track which users have acknowledged the notification.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="broadcast_acknowledgements"
    )
    broadcast = models.ForeignKey(
        BroadcastNotification,
        on_delete=models.CASCADE,
        related_name="acknowledgements"
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="broadcast_acknowledgements"
    )
    event_type = models.CharField(
        max_length=100, choices=EventType.choices()
    )
    acknowledged_at = models.DateTimeField(default=now)
    via_channel = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Channel via which user acknowledged (e.g., in_app, email)"
    )

    class Meta:
        unique_together = ('user', 'broadcast')
        verbose_name = 'Broadcast Acknowledgement'
        verbose_name_plural = 'Broadcast Acknowledgements'
        indexes = [
            models.Index(fields=['user', 'broadcast']),
            models.Index(fields=['website']),
        ]
        ordering = ['-acknowledged_at']

    def __str__(self):
        return f"Ack: {self.user} -> {self.broadcast.title}"
    
    def is_visible_to(self, user):
        if self.show_to_all:
            return True
        user_roles = getattr(user, 'roles', [])
        return bool(set(self.target_roles) & set(user_roles))


class BroadcastOverride(models.Model):
    """
    Represents an override for a broadcast notification.
    This allows specific users or roles to receive or
    ignore a broadcast notification.
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

    force_channels = ArrayField(models.CharField(
        max_length=50, choices=NotificationType.choices()
    ))

    override_config = models.JSONField(
        default=dict, blank=True,
        help_text=(
            "Custom configuration for this override, e.g. priority, category, message, title"
        )
    )
    is_active = models.BooleanField(default=True)


    event_type = models.CharField(
        max_length=100, choices=EventType.choices()
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Broadcast Override'
        verbose_name_plural = 'Broadcast Overrides'
        unique_together = ('website', 'broadcast', 'user', 'role')
        ordering = ['-created_at']
        
        indexes = [
            models.Index(fields=['website', 'broadcast', 'user', 'role']),
        ]

    def __str__(self):
        return f"Override: {self.user} -> {self.broadcast.title}"
    
    def get_effective_channels_for(self, user):
        """ Returns the effective channels for this broadcast override.
        If an override exists for the user, it returns the forced channels.
        Otherwise, it returns the broadcast's default channels.
        """
        override = BroadcastOverride.objects.filter(
            broadcast=self, user=user, is_active=True
        ).first()

        if override:
            return override.force_channels
        return self.channels