"""
Announcement models for the Announcements Center feature.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from notifications_system.models.broadcast_notification import BroadcastNotification
from websites.models import Website

User = settings.AUTH_USER_MODEL


class Announcement(models.Model):
    """
    Announcement model that extends BroadcastNotification functionality
    with announcement-specific features like categories, featured images,
    and engagement tracking.
    """
    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('update', 'System Update'),
        ('maintenance', 'Maintenance'),
        ('promotion', 'Promotion'),
        ('general', 'General'),
    ]

    # Link to broadcast notification
    broadcast = models.OneToOneField(
        BroadcastNotification,
        on_delete=models.CASCADE,
        related_name='announcement',
        null=True,
        blank=True,
        help_text="Linked broadcast notification"
    )

    # Announcement-specific fields
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text="Category of the announcement"
    )

    featured_image = models.ImageField(
        upload_to='announcements/',
        null=True,
        blank=True,
        help_text="Featured image for the announcement"
    )

    read_more_url = models.URLField(
        null=True,
        blank=True,
        help_text="Optional URL for 'Read More' link"
    )

    # Engagement tracking
    view_count = models.IntegerField(
        default=0,
        help_text="Total number of views"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['broadcast']),  # For join optimization
        ]

    def __str__(self):
        if self.broadcast:
            return f"Announcement: {self.broadcast.title}"
        return f"Announcement #{self.id}"

    @property
    def title(self):
        """Get title from linked broadcast."""
        return self.broadcast.title if self.broadcast else ""

    @property
    def message(self):
        """Get message from linked broadcast."""
        return self.broadcast.message if self.broadcast else ""

    @property
    def is_pinned(self):
        """Check if announcement is pinned."""
        return self.broadcast.pinned if self.broadcast else False

    @property
    def is_active(self):
        """Check if announcement is active."""
        return self.broadcast.is_active if self.broadcast else False

    @property
    def website(self):
        """Get website from linked broadcast."""
        return self.broadcast.website if self.broadcast else None

    @property
    def target_roles(self):
        """Get target roles from linked broadcast."""
        return self.broadcast.target_roles if self.broadcast else []


class AnnouncementView(models.Model):
    """
    Tracks when a user views an announcement.
    Used for engagement analytics.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='announcement_views'
    )

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='views'
    )

    viewed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the user viewed the announcement"
    )

    time_spent = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time spent viewing in seconds"
    )

    acknowledged = models.BooleanField(
        default=False,
        help_text="Whether user acknowledged the announcement"
    )

    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the user acknowledged the announcement"
    )

    class Meta:
        unique_together = ('user', 'announcement')
        verbose_name = 'Announcement View'
        verbose_name_plural = 'Announcement Views'
        indexes = [
            models.Index(fields=['user', 'announcement']),  # For unread count queries (most important)
            models.Index(fields=['announcement', 'viewed_at']),
            models.Index(fields=['user', 'viewed_at']),
            models.Index(fields=['announcement', 'acknowledged']),
            models.Index(fields=['user', 'acknowledged']),  # For analytics
        ]
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.email} viewed {self.announcement}"

