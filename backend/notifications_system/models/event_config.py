from django.db import models
from notifications_system.enums import NotificationPriority


class NotificationEventConfig(models.Model):
    """
    Registry entry for a notification event.
    Defines default behavior, supported channels, target roles,
    and whether users/admins can override preferences for this event.

    One row per event_key. Seeded from JSON config, managed via admin.
    """

    event_key = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique event identifier e.g. 'order.completed'",
    )
    label = models.CharField(
        max_length=255,
        help_text="Human-readable name shown in UI e.g. 'Order Completed'",
    )
    description = models.TextField(
        blank=True,
        help_text="Explains to users what triggers this notification.",
    )

    # Channel support
    supports_email = models.BooleanField(default=True)
    supports_in_app = models.BooleanField(default=True)

    # Default channel state — can be overridden by user/admin preferences
    default_email_enabled = models.BooleanField(default=True)
    default_in_app_enabled = models.BooleanField(default=True)

    # Priority
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    # Who receives this event
    # Stored as a list of role strings e.g. ['client', 'writer']
    recipient_roles = models.JSONField(
        default=list,
        help_text="Roles that receive this event e.g. ['client', 'writer']",
    )

    # Control
    is_mandatory = models.BooleanField(
        default=False,
        help_text=(
            "If True, always sent regardless of user preferences. "
            "Use for critical events like account suspension."
        ),
    )
    user_can_disable = models.BooleanField(
        default=True,
        help_text="Whether users can turn this notification off.",
    )
    admin_can_disable = models.BooleanField(
        default=True,
        help_text="Whether admins can disable this for their website.",
    )

    # Digest
    digest_eligible = models.BooleanField(
        default=False,
        help_text="Whether this event can be grouped into a digest.",
    )
    digest_group = models.CharField(
        max_length=100,
        blank=True,
        help_text="Digest group key e.g. 'daily_summary'",
    )

    # Website override
    is_overridable_per_website = models.BooleanField(
        default=True,
        help_text=(
            "If True, websites can override template and default channel "
            "settings for this event."
        ),
    )

    # Cooldown — prevent the same event firing too frequently for a user
    cooldown_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Minimum seconds between sends of this event to the same user. 0 = no cooldown.",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Event Config'
        verbose_name_plural = 'Notification Event Configs'
        ordering = ['event_key']

    def __str__(self):
        return f"{self.label} ({self.event_key})"

    def get_default_channels(self):
        """Returns list of channels enabled by default for this event."""
        channels = []
        if self.supports_email and self.default_email_enabled:
            channels.append('email')
        if self.supports_in_app and self.default_in_app_enabled:
            channels.append('in_app')
        return channels

    def is_enabled_for_channel(self, channel):
        """Check if a specific channel is supported and enabled by default."""
        if channel == 'email':
            return self.supports_email and self.default_email_enabled
        if channel == 'in_app':
            return self.supports_in_app and self.default_in_app_enabled
        return False