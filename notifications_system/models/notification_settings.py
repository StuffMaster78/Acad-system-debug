from django.db import models
from django.conf import settings
from websites.models import Website
from users.mixins import UserRole   
from django.contrib.postgres.fields import JSONField


class NotificationSystemSettings(models.Model):
    """
    Stores global settings like fallback rules and max retries.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
    )
    fallback_rules = JSONField(default=dict, blank=True)
    max_retries_per_channel = JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Global Notification Settings"
        verbose_name_plural = "Global Notification Settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # Enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        return cls.objects.get_or_create(pk=1)[0]