


from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from fines.models import Fine

User = settings.AUTH_USER_MODEL 


class WebhookPlatform(models.TextChoices):
    """Available platforms for webhooks."""
    SLACK = "slack", "Slack"
    DISCORD = "discord", "Discord"
    TELEGRAM = "telegram", "Telegram"


class WebhookSettings(models.Model):
    """
    Stores webhook settings for a writer.
    """
    from orders.order_enums import WebhookEvent

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="webhook_settings",
        help_text="The user this webhook setting belongs to."
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="webhook_settings",
        help_text="Multitenancy support: this webhook is for a specific website."
    )
    platform = models.CharField(
        max_length=20,
        choices=WebhookPlatform.choices,
        help_text="The platform for the webhook (e.g., Slack, Discord)."
    )
    webhook_url = models.URLField(
        help_text="The URL to which the webhook will send requests."
    )
    enabled = models.BooleanField(
        default=True,
        help_text="If false, this webhook won't send any events."
    )
    subscribed_events = ArrayField(
        models.CharField(
            max_length=50,
            choices=WebhookEvent.choices
        ),
        default=list,
        blank=True,
        help_text="List of events this webhook is subscribed to."
    )
    is_active = models.BooleanField(
        default=True,
        help_text= (
            "Soft delete flag — deactivates the webhook "
            "without removing the record."
        )
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "platform", "website")
        verbose_name = "Webhook Setting"
        verbose_name_plural = "Webhook Settings"

    def __str__(self):
        return f"{self.user} - {self.platform} webhook"