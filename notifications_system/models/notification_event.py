from django.db import models
from websites.models import Website


class NotificationEvent(models.Model):
    """
    Represents a specific event that can trigger notifications.
    Examples include "order.assigned", "payment.failed", etc.
    This allows for dynamic event handling and notification triggering.
    """

    event = models.CharField(max_length=100, unique=True)
    event_key = models.CharField(
        max_length=100, unique=True,
        help_text="Unique key for the event, e.g. 'order.created'"
    )
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100, blank=True) # e.g. "order", "payment"
    enabled_by_default = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    website = models.ForeignKey(
        Website, null=True, blank=True,
        on_delete=models.CASCADE,
        related_name="notification_events",
        help_text="The website this event is associated with."
    )

    is_active = models.BooleanField(default=True)
    is_critical = models.BooleanField(default=False)
    # version = models.CharField(max_length=10, default="v1.0")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event} ({self.name})"