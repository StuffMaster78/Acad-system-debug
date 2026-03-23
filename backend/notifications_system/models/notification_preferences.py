from django.db import models
from django.conf import settings
from django.utils import timezone
from notifications_system.enums import (
    NotificationChannel,
    NotificationPriority,
    DigestFrequency,
)


class NotificationPreferenceProfile(models.Model):
    """
    Reusable preference template created by admins.
    Can be applied to individual users or entire roles.
    Acts as the default when a user has no explicit preference set.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notification_preference_profiles',
        help_text="Null = global profile available to all websites.",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Channel defaults
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)

    # DND defaults
    dnd_enabled = models.BooleanField(default=False)
    dnd_start_hour = models.PositiveSmallIntegerField(
        default=22,
        help_text="Hour (0-23) when DND starts.",
    )
    dnd_end_hour = models.PositiveSmallIntegerField(
        default=6,
        help_text="Hour (0-23) when DND ends.",
    )

    # Digest defaults
    digest_enabled = models.BooleanField(default=False)
    digest_frequency = models.CharField(
        max_length=20,
        choices=DigestFrequency.choices,
        default=DigestFrequency.DAILY,
        blank=True,
    )

    is_default = models.BooleanField(
        default=False,
        help_text="If True, applied to new users on this website automatically.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_preference_profiles',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Preference Profile'
        verbose_name_plural = 'Notification Preference Profiles'
        unique_together = ('website', 'name')

    def __str__(self):
        scope = self.website.name if self.website else 'Global'
        return f"{self.name} ({scope})"


class NotificationPreference(models.Model):
    """
    Per-user, per-website master notification preferences.
    Controls channel access, DND, muting, and digest behavior.
    One row per user per website.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='user_notification_preferences',
    )

    # Applied profile — used as fallback for unset fields
    profile = models.ForeignKey(
        NotificationPreferenceProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applied_preferences',
        help_text="Profile applied to this user. Individual fields override profile defaults.",
    )

    # Channel toggles
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)

    # DND
    dnd_enabled = models.BooleanField(default=False)
    dnd_start_hour = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Hour (0-23) when DND starts.",
    )
    dnd_end_hour = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Hour (0-23) when DND ends.",
    )

    # Muting
    mute_all = models.BooleanField(
        default=False,
        help_text="Suppress all notifications. Useful during maintenance.",
    )
    mute_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Suppress all notifications until this datetime.",
    )

    # Digest
    digest_enabled = models.BooleanField(default=False)
    digest_only = models.BooleanField(
        default=False,
        help_text="If True, only receive digest notifications — no immediate sends.",
    )
    digest_frequency = models.CharField(
        max_length=20,
        choices=DigestFrequency.choices,
        default=DigestFrequency.DAILY,
        blank=True,
    )

    # Minimum priority — notifications below this are suppressed
    min_priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
        unique_together = ('user', 'website')
        indexes = [
            models.Index(fields=['user', 'website']),
        ]

    def __str__(self):
        return f"Preferences for {self.user} on {self.website}"

    def is_muted(self):
        """Returns True if all notifications are currently suppressed."""
        if self.mute_all:
            return True
        if self.mute_until and self.mute_until > timezone.now():
            return True
        return False

    def is_in_dnd(self):
        """Returns True if current time falls within DND hours."""
        if not self.dnd_enabled:
            return False
        if self.dnd_start_hour is None or self.dnd_end_hour is None:
            return False
        current_hour = timezone.localtime().hour
        if self.dnd_start_hour <= self.dnd_end_hour:
            return self.dnd_start_hour <= current_hour < self.dnd_end_hour
        # Overnight DND e.g. 22:00 - 06:00
        return current_hour >= self.dnd_start_hour or current_hour < self.dnd_end_hour

    def get_active_channels(self):
        """Returns list of currently enabled channels."""
        channels = []
        if self.email_enabled:
            channels.append(NotificationChannel.EMAIL)
        if self.in_app_enabled:
            channels.append(NotificationChannel.IN_APP)
        return channels


class NotificationEventPreference(models.Model):
    """
    Per-user, per-event channel preferences.
    Overrides the master NotificationPreference for specific events.
    e.g. user wants all notifications by email except order.assigned — in-app only.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_notification_preferences',
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='event_notification_preferences',
    )
    event = models.ForeignKey(
        'notifications_system.NotificationEvent',
        on_delete=models.CASCADE,
        related_name='user_preferences',
    )

    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    digest_enabled = models.BooleanField(default=False)

    # If False, this event is completely silenced for this user
    is_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Event Preference'
        verbose_name_plural = 'Notification Event Preferences'
        unique_together = ('user', 'website', 'event')
        indexes = [
            models.Index(fields=['user', 'website', 'is_enabled']),
        ]

    def __str__(self):
        return f"{self.user} — {self.event.event_key} on {self.website}"


class RoleNotificationPreference(models.Model):
    """
    Default notification preferences per role per website.
    Used as fallback when a user has no NotificationPreference set.
    Admins configure these — they apply to all users of that role
    unless overridden at the user level.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='role_notification_preferences',
    )
    role = models.CharField(
        max_length=50,
        help_text="Role these defaults apply to e.g. 'writer', 'client'",
    )

    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    digest_enabled = models.BooleanField(default=False)
    min_priority = models.CharField(
        max_length=20,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Role Notification Preference'
        verbose_name_plural = 'Role Notification Preferences'
        unique_together = ('role', 'website')

    def __str__(self):
        return f"{self.role} defaults on {self.website}"