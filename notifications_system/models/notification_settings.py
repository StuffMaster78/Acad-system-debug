from django.db import models
from django.conf import settings
from websites.models import Website
from users.mixins import UserRole   
from django.contrib.postgres.fields import JSONField


class UserNotificationSettings(models.Model):
    """
    Stores global settings like fallback rules and max retries.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_system_settings"
    )
    # DND
    do_not_disturb_start = models.TimeField(null=True, blank=True)
    do_not_disturb_end = models.TimeField(null=True, blank=True)
    do_not_disturb_enabled = models.BooleanField(default=False)
    do_not_disturb_until = models.TimeField(null=True, blank=True)
    # Mute settings
    mute_all = models.BooleanField(default=False)
    mute_until = models.DateTimeField(null=True, blank=True)
    muted_events = models.JSONField(default=list, blank=True)
    # Digest settings
    digest_enabled = models.BooleanField(default=False)
    digest_only = models.BooleanField(default=False)
    fall_back_to_digest = models.BooleanField(default=False)
    digest_type = models.CharField(
        max_length=20,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly')],
        default='daily'
    )
    digest_time = models.TimeField(null=True, blank=True)
    digest_days = models.JSONField(default=list, blank=True)
    # TimeStamp settings
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Notification Settings"
        verbose_name_plural = "User Notification Settings"
        unique_together = ('website', 'user')

    def save(self, *args, **kwargs):
        self.pk = 1  # Enforce singleton
        super().save(*args, **kwargs)


class GlobalNotificationSystemSettings(models.Model):
    """ 
    Stores global settings for the notification system.
    This includes fallback rules, max retries,
    and other system-wide configurations.
    """
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="global_notification_settings"
    )
    fallback_rules = models.JSONField(default=dict, blank=True)
    max_retries_per_channel = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Global Notification System Settings"
        verbose_name_plural = "Global Notification System Settings"
        unique_together = ('website',)

    def save(self, *args, **kwargs):
        self.pk = 1  # Enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        return cls.objects.get_or_create(pk=1)[0]