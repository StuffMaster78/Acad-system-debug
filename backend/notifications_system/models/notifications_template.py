from django.conf import settings
from django.db import models
from notifications_system.enums import NotificationChannel
from notifications_system.models.notification_event import NotificationEvent

class NotificationTemplate(models.Model):
    """Templates per event/channel/locale/version, with optional tenant override."""
    event = models.ForeignKey(
        NotificationEvent, on_delete=models.CASCADE, related_name="templates"
    )
    website = models.ForeignKey(
        "websites.Website", null=True, blank=True, on_delete=models.CASCADE
    )
    channel = models.CharField(max_length=16, choices=NotificationChannel.choices)
    locale = models.CharField(max_length=10, default="en")
    version = models.PositiveIntegerField(default=1)
    subject = models.CharField(max_length=200, blank=True)
    body_html = models.TextField(blank=True)
    body_text = models.TextField(blank=True)
    provider_overrides = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "notif_template"
        unique_together = (("event", "website", "channel", "locale", "version"),)
        indexes = [models.Index(fields=["channel", "locale"])]

    def __str__(self) -> str:
        return f"{self.event.key}:{self.channel}:{self.locale}@{self.version}"