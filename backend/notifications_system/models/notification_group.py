from django.db import models

class NotificationGroup(models.Model):
    """ Represents a group of notifications with shared settings.
    Example: A group for 'Daily Summaries' or 'Weekly Reports'.
    This allows for easier management of notification
    settings across multiple notifications.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="notification_groups"
    )
    users = models.ManyToManyField(
        'users.User',
        related_name="notification_groups",
        help_text="Users who are part of this notification group."
    )
    channels = models.CharField(
        max_length=100,
        help_text="Comma-separated list of channels for this group, e.g. 'email,in_app'"
    )
    is_active = models.BooleanField(default=True, help_text="Is this group active?")
    
    default_channel = models.CharField(max_length=30, default="in_app")  # or Enum
    default_priority = models.CharField(max_length=30, default="normal")  # or Enum
    is_enabled_by_default = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
