from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _


class NotificationEventOverride(models.Model):
    """
    Stores database-level overrides for specific notification events.

    This model allows admins to override the default JSON config for 
    notifications on a per-event basis. Useful for dynamic control of 
    delivery without redeploying code.
    """

    website = models.ForeignKey(
        "core.Website",  # or whatever your Website model is
        on_delete=models.CASCADE,
        related_name="notification_event_overrides",
        null=True,  # null = global config
        blank=True,
        help_text="Scope override to a specific website or leave null for global."
    )

    event_key = models.CharField(
        max_length=128,
        db_index=True,
        help_text="Unique identifier for the event (e.g. user.password_reset_requested)."
    )

    enabled = models.BooleanField(
        default=True,
        help_text="Whether this override is active. Overrides default config."
    )

    priority = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text="Override the priority (e.g. high, medium, low)."
    )

    channels = ArrayField(
        base_field=models.CharField(max_length=32),
        blank=True,
        null=True,
        help_text="Override delivery channels (e.g. ['email', 'dashboard'])."
    )

    roles = ArrayField(
        base_field=models.CharField(max_length=64),
        blank=True,
        null=True,
        help_text="Restrict who can receive this notification (e.g. ['client', 'support'])."
    )

    fallback_message = models.TextField(
        blank=True,
        null=True,
        help_text="Fallback plain text message if no template renders."
    )

    template_key = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Override the template key for message rendering."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Notification Event Override")
        verbose_name_plural = _("Notification Event Overrides")
        unique_together = ("website", "event_key")

    def __str__(self):
        return f"[{self.website or 'GLOBAL'}] {self.event_key}"