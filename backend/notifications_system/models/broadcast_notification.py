from django.db import models
from django.utils import timezone
from django.conf import settings
from websites.models.websites import Website
from notifications_system.enums import (
    NotificationChannel,
    NotificationEvent,
)


class BroadcastNotification(models.Model):
    """
    A notification broadcast to multiple users — system-wide
    or website-wide announcements and alerts.
    """
    title = models.CharField(max_length=255)
    message = models.TextField()
    event_type = models.CharField(
        max_length=100,
        default=NotificationEvent.ADMIN_BROADCAST,
        help_text="Event key e.g. 'system.broadcast'",
    )

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='broadcast_notifications',
    )

    # Targeting
    show_to_all = models.BooleanField(default=False)
    target_roles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of roles that should receive this broadcast.",
    )

    # Channels
    channels = models.JSONField(
        default=list,
        help_text="Delivery channels e.g. ['in_app', 'email']",
    )

    # Behavior
    is_optional = models.BooleanField(
        default=False,
        help_text="If True, respects user notification preferences.",
    )
    is_blocking = models.BooleanField(default=True)
    require_acknowledgement = models.BooleanField(default=True)
    pinned = models.BooleanField(default=False)
    dismissible = models.BooleanField(default=True)
    show_in_dashboard = models.BooleanField(default=True)

    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_broadcasts',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-pinned', '-created_at']
        verbose_name = 'Broadcast Notification'
        verbose_name_plural = 'Broadcast Notifications'
        unique_together = ('website', 'title', 'event_type')
        indexes = [
            models.Index(fields=['website', 'event_type']),
            models.Index(fields=['is_active', 'scheduled_for']),
        ]

    def __str__(self):
        return f"[{self.website}] {self.title}"

    @property
    def is_expired(self):
        return bool(self.expires_at and self.expires_at < timezone.now())

    def is_visible_to(self, user):
        """Check whether this broadcast should be shown to a given user."""
        if self.show_to_all:
            return True
        user_role = getattr(user, 'role', None)
        return user_role in self.target_roles


class BroadcastAcknowledgement(models.Model):
    """
    Tracks which users have acknowledged a broadcast notification.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='broadcast_acknowledgements',
    )
    broadcast = models.ForeignKey(
        BroadcastNotification,
        on_delete=models.CASCADE,
        related_name='acknowledgements',
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='broadcast_acknowledgements',
    )
    via_channel = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Channel through which the user acknowledged e.g. in_app, email",
    )
    acknowledged_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'broadcast')
        verbose_name = 'Broadcast Acknowledgement'
        verbose_name_plural = 'Broadcast Acknowledgements'
        ordering = ['-acknowledged_at']
        indexes = [
            models.Index(fields=['user', 'broadcast']),
            models.Index(fields=['website']),
        ]

    def __str__(self):
        return f"{self.user} acknowledged '{self.broadcast.title}'"


class BroadcastOverride(models.Model):
    """
    Per-user override for a broadcast notification.
    Forces specific channels regardless of user preferences.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='broadcast_overrides',
    )
    broadcast = models.ForeignKey(
        BroadcastNotification,
        on_delete=models.CASCADE,
        related_name='overrides',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='broadcast_overrides',
    )

    # Role this override applies to — stored as string, not FK to User
    role = models.CharField(
        max_length=50,
        blank=True,
        help_text="If set, applies to all users with this role.",
    )

    force_channels = models.JSONField(
        default=list,
        help_text="Channels to force for this user/role.",
    )
    override_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extra config e.g. priority, custom message.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Broadcast Override'
        verbose_name_plural = 'Broadcast Overrides'
        unique_together = ('website', 'broadcast', 'user')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['website', 'broadcast', 'user']),
        ]

    def __str__(self):
        return f"Override for {self.user} on '{self.broadcast.title}'"

    def get_effective_channels(self):
        """
        Returns forced channels if override is active,
        otherwise falls back to the broadcast's default channels.
        """
        if self.is_active and self.force_channels:
            return self.force_channels
        return self.broadcast.channels