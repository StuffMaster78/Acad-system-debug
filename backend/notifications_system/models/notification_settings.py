from django.db import models


class GlobalNotificationSystemSettings(models.Model):
    """
    System-wide notification defaults for a website.
    One row per website — controls fallback rules, retry limits,
    and platform-level channel configuration.

    Individual user preferences override these at the user level.
    NotificationPreferenceProfile overrides these at the profile level.
    """

    # OneToOneField enforces one settings row per website cleanly
    website = models.OneToOneField(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='notification_system_settings',
    )

    # Channel availability — admin can disable a channel platform-wide
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)

    # Email sender identity for this website
    email_from_name = models.CharField(max_length=255, blank=True)
    email_from_address = models.EmailField(blank=True)
    email_reply_to = models.EmailField(blank=True)
    email_noreply_address = models.EmailField(
        blank=True,
        default="",
        help_text="Optional no-reply email address for outbound mail.",
    )

    # Email provider override — null means use platform default
    email_provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="Provider slug e.g. 'sendgrid', 'mailgun', 'ses'. "
                  "Leave blank to use platform default.",
    )
    email_provider_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider credentials and config. Encrypted at rest.",
    )

    # Fallback chain — if channel fails, try next
    # Structure: {"email": "in_app", "in_app": null}
    fallback_rules = models.JSONField(
        default=dict,
        blank=True,
        help_text="Channel fallback chain e.g. {'email': 'in_app'}",
    )

    # Per-channel retry limits
    # Structure: {"email": 3, "in_app": 1}
    max_retries_per_channel = models.JSONField(
        default=dict,
        blank=True,
        help_text="Max delivery retries per channel e.g. {'email': 3}",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Global Notification System Settings'
        verbose_name_plural = 'Global Notification System Settings'

    def __str__(self):
        return f"Notification settings for {self.website}"

    @classmethod
    def for_website(cls, website):
        """
        Returns settings for a website, creating defaults if none exist.
        Always use this instead of get() or filter() directly.
        """
        obj, _ = cls.objects.get_or_create(website=website)
        return obj

    def get_fallback_for_channel(self, channel):
        """Returns the fallback channel for a given channel, or None."""
        return self.fallback_rules.get(channel)

    def get_max_retries_for_channel(self, channel, default=3):
        """Returns max retries for a given channel."""
        return self.max_retries_per_channel.get(channel, default)