from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class DashboardNotification(models.Model):
    """
    Model for storing dashboard notifications shown within the app UI.

    Notifications are targeted to individual users and are stored for 
    persistence and audit. These may originate from various system 
    events (e.g., order submitted, user verified, payment refunded).

    Attributes:
        user (User): The user receiving the notification.
        event_key (str): A system-wide identifier for the triggering event.
        title (str): Title or short summary of the notification.
        message (str): Main body or description of the notification.
        is_read (bool): Whether the user has read the notification.
        created_at (datetime): Timestamp when the notification was created.
        updated_at (datetime): Timestamp when the notification was last updated.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dashboard_notifications",
        help_text="The user who receives this notification.",
    )
    event_key = models.CharField(
        max_length=100,
        help_text="Event key that triggered this notification.",
    )
    title = models.CharField(
        max_length=255,
        help_text="Short title or summary of the notification.",
    )
    message = models.TextField(
        help_text="Full message content of the notification.",
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Flag indicating whether the notification has been read.",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Time when the notification was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Time when the notification was last updated.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Dashboard Notification"
        verbose_name_plural = "Dashboard Notifications"

    def mark_as_read(self):
        """
        Marks this notification as read and saves the change.
        """
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read", "updated_at"])

    def __str__(self):
        """
        Returns a human-readable representation of the notification.
        """
        return f"{self.title} for {self.user} ({'read' if self.is_read else 'unread'})"