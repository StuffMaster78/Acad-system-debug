from django.db import models
from django.conf import settings
from django.utils import timezone
from notifications_system.enums import NotificationPriority


class NotificationsUserStatus(models.Model):
    """
    Per-user status for a specific notification.
    Tracks read state, acknowledgement, and pinning.
    One row per user per notification.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_statuses',
    )
    notification = models.ForeignKey(
        'notifications_system.Notification',
        on_delete=models.CASCADE,
        related_name='user_statuses',
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='notification_user_statuses',
    )

    # Read state
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Acknowledgement — for notifications requiring explicit confirmation
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    # Pinning — user or staff can pin important notifications
    is_pinned = models.BooleanField(default=False)
    pinned_at = models.DateTimeField(null=True, blank=True)
    pinned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pinned_notification_statuses',
        help_text="Staff member who pinned this, or null if self-pinned.",
    )

    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Notification Status'
        verbose_name_plural = 'User Notification Statuses'
        unique_together = ('user', 'notification')
        indexes = [
            models.Index(fields=['user', 'website', 'is_read']),
            models.Index(fields=['user', 'website', 'is_acknowledged']),
            models.Index(fields=['user', 'is_pinned']),
            models.Index(fields=['notification', 'priority']),
        ]

    def __str__(self):
        return f"{self.user} — {self.notification} [{self.priority}]"

    def mark_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at', 'updated_at'])

    def acknowledge(self):
        """Mark notification as acknowledged."""
        if not self.is_acknowledged:
            self.is_acknowledged = True
            self.acknowledged_at = timezone.now()
            self.save(update_fields=['is_acknowledged', 'acknowledged_at', 'updated_at'])

    def pin(self, pinned_by=None):
        """Pin this notification for the user."""
        self.is_pinned = True
        self.pinned_at = timezone.now()
        self.pinned_by = pinned_by
        self.save(update_fields=['is_pinned', 'pinned_at', 'pinned_by', 'updated_at'])

    def unpin(self):
        """Unpin this notification."""
        self.is_pinned = False
        self.pinned_at = None
        self.pinned_by = None
        self.save(update_fields=['is_pinned', 'pinned_at', 'pinned_by', 'updated_at'])