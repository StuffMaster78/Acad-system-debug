from django.conf import settings
from django.db import models
from django.utils import timezone


class UserNotificationMeta(models.Model):
    """
    Per-user, per-website notification metadata.
    Tracks last seen timestamp and unread counts to avoid
    expensive COUNT queries on every page load.

    Updated by:
    - last_seen_at: when user opens their notification feed
    - unread_count: incremented on new notification, reset on mark-all-read
    - last_emailed_at: when the last digest or email notification was sent
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_meta',
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='user_notification_meta',
    )

    # When the user last opened their notification feed
    last_seen_at = models.DateTimeField(default=timezone.now)

    # Cached unread count — avoids COUNT(*) on every request
    unread_count = models.PositiveIntegerField(default=0)

    # When the last email or digest was sent to this user
    last_emailed_at = models.DateTimeField(null=True, blank=True)

    # When the last in-app notification was delivered
    last_notified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Notification Meta'
        verbose_name_plural = 'User Notification Meta'
        db_table = 'user_notification_meta'
        unique_together = ('user', 'website')
        indexes = [
            models.Index(fields=['user', 'website']),
        ]

    def __str__(self):
        return f"NotifMeta — {self.user_id} on {self.website_id}"

    def touch(self):
        """Record that the user checked their notification feed."""
        self.last_seen_at = timezone.now()
        self.save(update_fields=['last_seen_at', 'updated_at'])

    def increment_unread(self):
        """Increment unread count when a new notification arrives."""
        self.__class__.objects.filter(pk=self.pk).update(
            unread_count=models.F('unread_count') + 1
        )

    def reset_unread(self):
        """Reset unread count when user marks all as read."""
        self.unread_count = 0
        self.save(update_fields=['unread_count', 'updated_at'])

    def record_email_sent(self):
        """Record when an email or digest was sent."""
        self.last_emailed_at = timezone.now()
        self.save(update_fields=['last_emailed_at', 'updated_at'])