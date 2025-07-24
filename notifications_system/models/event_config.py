from django.db import models

class NotificationEventConfig(models.Model):
    """Model for storing notification event configurations."""
    event_key = models.CharField(max_length=255, unique=True)
    config_json = models.JSONField()

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notification Event Config Override"
        verbose_name_plural = "Notification Event Config Overrides"

    def __str__(self):
        return self.event_key