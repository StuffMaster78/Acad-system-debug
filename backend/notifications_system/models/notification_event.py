from django.db import models
from notifications_system.enums import NotificationCategory


class NotificationEvent(models.Model):
    """
    Registry of all notification events in the system.
    One row per event type — defines what the event is, not how it behaves.
    Behavior is defined in NotificationEventConfig.
    Seeded from JSON config on deploy, manageable via admin.

    Examples: 'order.completed', 'wallet.credited', 'account.suspended'
    """
    event_key = models.CharField(
        max_length=128,
        unique=True,
        help_text="Unique dot-notation identifier e.g. 'order.completed'",
    )
    label = models.CharField(
        max_length=128,
        help_text="Human-readable name e.g. 'Order Completed'",
    )
    description = models.TextField(
        blank=True,
        help_text="What triggers this event. Shown to users in preference settings.",
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        choices=NotificationCategory.choices,
        help_text="Grouping category e.g. 'order', 'payment', 'account'",
    )

    # Scope defines who this event is relevant to
    SCOPE_USER = 'user'
    SCOPE_WEBSITE = 'website'
    SCOPE_SYSTEM = 'system'
    SCOPE_CHOICES = [
        (SCOPE_USER, 'User'),
        (SCOPE_WEBSITE, 'Website'),
        (SCOPE_SYSTEM, 'System'),
    ]
    scope = models.CharField(
        max_length=16,
        choices=SCOPE_CHOICES,
        default=SCOPE_USER,
        help_text="Who this event targets — a user, a website, or the whole system.",
    )

    schema_version = models.PositiveIntegerField(
        default=1,
        help_text="Incremented when the event payload schema changes.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional extra data about this event for tooling or documentation.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive events are ignored by the notification system.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Event'
        verbose_name_plural = 'Notification Events'
        ordering = ['category', 'event_key']
        indexes = [
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.label} ({self.event_key})"