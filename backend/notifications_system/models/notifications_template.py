from django.conf import settings
from django.db import models
from notifications_system.enums import (
    NotificationChannel, TemplateScope
)

class NotificationTemplate(models.Model):
    """
    Rendered template per event, channel, locale, and version.
    Null website = global template used as default.
    Website-specific templates override the global one for that tenant.

    Resolution order:
        1. Website-specific template (matching locale + latest version)
        2. Global template (matching locale + latest version)
        3. Global template (default locale 'en')
    """
    event = models.ForeignKey(
        'notifications_system.NotificationEvent',
        on_delete=models.CASCADE,
        related_name='templates',
    )
    website = models.ForeignKey(
        'websites.Website',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notification_templates',
        help_text="Null = global template. Set to override for a specific website.",
    )
    scope = models.CharField(
        max_length=20,
        choices=TemplateScope.choices,
        default=TemplateScope.GLOBAL,
    )

    channel = models.CharField(
        max_length=16,
        choices=NotificationChannel.choices,
    )
    locale = models.CharField(
        max_length=10,
        default='en',
        help_text="Locale code e.g. 'en', 'fr', 'es'",
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Increment when making breaking changes to the template.",
    )

    # Email fields
    subject = models.CharField(
        max_length=255,
        blank=True,
        help_text="Email subject line. Supports template variables e.g. {{user_name}}",
    )
    body_html = models.TextField(
        blank=True,
        help_text="HTML email body. Supports template variables.",
    )
    body_text = models.TextField(
        blank=True,
        help_text="Plain text fallback for email. Always provide this.",
    )

    # In-app fields
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="In-app notification title. Supports template variables.",
    )
    message = models.TextField(
        blank=True,
        help_text="In-app notification body. Supports template variables.",
    )

    # Available template variables for this template
    # e.g. ["user_name", "order_id", "website_name"]
    available_variables = models.JSONField(
        default=list,
        blank=True,
        help_text="List of context variables available for this template.",
    )

    # Provider-specific overrides
    # e.g. {"sendgrid": {"template_id": "d-xxxx"}}
    provider_overrides = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific config overrides e.g. SendGrid template ID.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Inactive templates are skipped during resolution.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_notification_templates',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notif_template'
        unique_together = (('event', 'website', 'channel', 'locale', 'version'),)
        ordering = ['-version']
        indexes = [
            models.Index(fields=['channel', 'locale']),
            models.Index(fields=['event', 'website', 'channel']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        scope = self.website.name if self.website else 'global'
        return f"{self.event.event_key}:{self.channel}:{self.locale}@v{self.version} ({scope})"

    def get_render_fields(self):
        """
        Returns the fields relevant to this template's channel for rendering.
        """
        if self.channel == NotificationChannel.EMAIL:
            return {
                'subject': self.subject,
                'body_html': self.body_html,
                'body_text': self.body_text,
            }
        if self.channel == NotificationChannel.IN_APP:
            return {
                'title': self.title,
                'message': self.message,
            }
        return {}