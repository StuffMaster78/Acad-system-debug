# notifications/models/notification_group.py
from django.db import models

class NotificationGroup(models.Model):
    """ Represents a group of notifications with shared settings.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    default_channel = models.CharField(max_length=30, default="in_app")  # or Enum
    default_priority = models.CharField(max_length=30, default="normal")  # or Enum
    is_enabled_by_default = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
