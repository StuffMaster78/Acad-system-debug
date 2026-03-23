from django.db import models
from django.utils.translation import gettext_lazy as _
from notifications_system.enums import NotificationPriority


class NotificationEventOverride(models.Model):
    """
    Per-website override for a notification event's default config.
    Only fields that are explicitly set on this override take effect —
    unset fields fall back to the base NotificationEventConfig.

    null website = global override applied across all websites.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='notification_event_overrides',
        null=True,
        blank=True,
        help_text="Scope to a specific website. Leave null for a global override.",
    )
    event_config = models.ForeignKey(
        'notifications_system.NotificationEventConfig',
        on_delete=models.CASCADE,
        related_name='overrides',
        help_text="The base event config this override applies to.",
    )

    # Shadowed from event_key on the config — kept for quick querying
    event_key = models.CharField(
        max_length=128,
        help_text="Denormalised from event_config.event_key for efficient filtering.",
        editable=False,  # always set from event_config
    )

    enabled = models.BooleanField(
        default=True,
        help_text="Whether this event is enabled for this website.",
    )
    priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        blank=True,
        help_text="Override the default priority. Leave blank to use event config default.",
    )

    # None = use event config default, [] = disable all channels
    channels = models.JSONField(
        null=True,
        blank=True,
        help_text="Override delivery channels e.g. ['email', 'in_app']. Null = use default.",
    )
    roles = models.JSONField(
        null=True,
        blank=True,
        help_text="Restrict recipient roles e.g. ['client', 'support']. Null = use default.",
    )

    template_key = models.CharField(
        max_length=128,
        blank=True,
        help_text="Override the template key for rendering. Leave blank to use default.",
    )
    fallback_message = models.TextField(
        blank=True,
        help_text="Fallback plain text message if no template renders.",
    )

    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_event_overrides',
        help_text="Admin who created this override.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Notification Event Override')
        verbose_name_plural = _('Notification Event Overrides')
        unique_together = ('website', 'event_config')
        ordering = ['event_key']

    def __str__(self):
        scope = self.website.name if self.website else 'GLOBAL'
        return f"[{scope}] {self.event_key}"

    def save(self, *args, **kwargs):
        # Keep event_key in sync with the related config
        if self.event_config_id and not self.event_key:
            self.event_key = self.event_config.event_key
        super().save(*args, **kwargs)

    def get_effective_channels(self):
        """
        Returns this override's channels if set,
        otherwise falls back to the base event config defaults.
        """
        if self.channels is not None:
            return self.channels
        return self.event_config.get_default_channels()

    def get_effective_priority(self):
        """Returns override priority or falls back to event config priority."""
        return self.priority or self.event_config.priority

    def get_effective_roles(self):
        """Returns override roles or falls back to event config recipient_roles."""
        if self.roles is not None:
            return self.roles
        return self.event_config.recipient_roles