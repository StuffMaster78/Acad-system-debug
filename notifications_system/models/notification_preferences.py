from datetime import timezone
from django.db import models
from django.utils.timezone import now
from core.models.base import WebsiteSpecificBaseModel
from django.conf import settings
from websites.models import User, Website
from notifications_system.enums import (
    DigestType,
    NotificationType,
    NotificationCategory,
    DeliveryStatus,
    EventType,
    NotificationPriority
)
from django.contrib.postgres.fields import ArrayField
from users.mixins import UserRole   
from django.contrib.postgres.fields import JSONField
from notifications_system.models.notification_preferences import UserNotificationPreference
from notifications_system.models.notification_event import NotificationEvent
from django.conf import settings

User = settings.AUTH_USER_MODEL

class UserNotificationPreference(models.Model):
    """
    Represents a user's notification preference.
    This allows users to set their own notification preferences.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="user_notification_preferences"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    mute_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Preferences for {self.user.username} on {self.website.domain}"
    
    class Meta:
        verbose_name = "User Notification Preference"
        verbose_name_plural = "User Notification Preferences"
        unique_together = ('website', 'user')
    
    def is_muted(self):
        return self.mute_until and self.mute_until > timezone.now()

class NotificationPreferenceGroup(models.Model):
    """
    Represents a group of notification preferences that can be applied to users.
    This allows for easier management of notification settings across multiple users.
    """
    website = models.ForeignKey("websites.Website", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    default_channels = ArrayField(
        models.CharField(max_length=20, choices=NotificationType.choices),
        default=list
    )
    quiet_hours = models.JSONField(default=dict, blank=True)  # {"start": "22:00", "end": "07:00"}
    is_active = models.BooleanField(default=True)
    website = models.ForeignKey("websites.Website", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
    
class NotificationEventPreference(models.Model):
    """
    Represents a user's preference for a specific notification event.
    This allows users to enable/disable notifications for specific events.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(NotificationEvent, on_delete=models.CASCADE)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    preference = models.ForeignKey(
        UserNotificationPreference,
        on_delete=models.CASCADE,
        related_name="event_preferences"
    )

    receive_email = models.BooleanField(default=True)
    receive_sms = models.BooleanField(default=False)
    receive_push = models.BooleanField(default=False)
    receive_in_app = models.BooleanField(default=True)
    receive_digest = models.BooleanField(default=True)


    class Meta:
        unique_together = ("user", "event", "website")

class NotificationPreference(models.Model):
    """
    User preferences for notifications.
    Allows for personalization and customization of notification settings.
    This model is used to manage how users receive notifications for different events and channels.
    It includes options for enabling/disabling notifications, setting do-not-disturb hours,
    and specifying notification frequency.
    It also supports multiple channels such as email, SMS, push notifications, and in-app notifications.
    Additionally, it allows for custom channels and overrides for specific events.
    This model is linked to a user and a website, allowing for website-specific notification settings.
    It also supports grouping of preferences for easier management.
    The model includes fields for enabling/disabling notifications, setting do-not-disturb hours,
    and specifying notification frequency.
    It also supports custom channels and overrides for specific events.
    It is designed to be flexible and extensible, allowing for future enhancements and additional features.
    It is used to manage user notification preferences across different websites and events.
    It is linked to a user and a website, allowing for website-specific notification settings.
    It supports multiple channels such as email, SMS, push notifications, and in-app notifications.
    It allows for custom channels and overrides for specific events.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="system_notifications_settings"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        help_text="The user whose preferences are being managed."
    )
    event = models.CharField(
        max_length=100,
        choices=EventType.choices,
        verbose_name=("Event Type")
    )
    channel = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        verbose_name=("Notification Channel")
    )
    profile = models.ForeignKey(
        'notifications_system.NotificationProfile',
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        help_text="The notification profile applied to this preference."
    )
    profile_group = models.ForeignKey(
        NotificationPreferenceGroup, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Are notifications enabled for this user?"
    )
    overrides = models.JSONField(default=dict) # e.g. { "order_created": false, "ticket_created": true }
    frequency = models.CharField(
        max_length=20,
        choices=[('immediate', 'Immediate'), ('daily', 'Daily'), ('weekly', 'Weekly')],
        default='immediate',
        help_text="Frequency of notifications."
    )
    do_not_disturb_start = models.TimeField(null=True, blank=True)
    do_not_disturb_end = models.TimeField(null=True, blank=True)
    do_not_disturb_until = models.TimeField(
        null=True,
        blank=True,
        help_text="Time until which notifications are muted."
    )
    receive_email = models.BooleanField(
        default=True,
        help_text="Allow email notifications."
    )
    receive_sms = models.BooleanField(
        default=False,
        help_text="Allow SMS notifications."
    )
    receive_push = models.BooleanField(
        default=True,
        help_text="Allow push notifications."
    )
    receive_in_app = models.BooleanField(
        default=True,
        help_text="Allow in-app notifications."
    )
    receive_digest = models.BooleanField(default=True)
    mute_all = models.BooleanField(
        default=False,
        help_text="Mute all notifications."
    )
    digest_only = models.BooleanField(
        default=False,
        help_text="Only receive notifications in digest form."
    )
    muted_events = models.JSONField(default=list, blank=True,
        help_text="List of events that are muted for this user."
    )
    channel_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Preferences for each channel, e.g. {'email': True, 'sms': False}"
    )
    custom_channels = ArrayField(models.CharField(
        max_length=20, choices=NotificationType.choices()),
        default=list, blank=True
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification Preference"
        verbose_name_plural = "Notification Preferences"
        unique_together = ('website', 'user', 'event', 'channel')
        indexes = [
            models.Index(fields=['website', 'user']),
            models.Index(fields=['event']),
            models.Index(fields=['channel']),
        ]

    def __str__(self):
        return f"Notification Preferences for {self.user.username}"
    

    def get_active_channels(self):
        return [
            channel for channel, enabled in {
                NotificationType.EMAIL: self.receive_email,
                NotificationType.SMS: self.receive_sms,
                NotificationType.PUSH: self.receive_push,
                NotificationType.IN_APP: self.receive_in_app,
            }.items() if enabled
        ]
    
    
    def as_dict(self):
        return {
            "receive_email": self.receive_email,
            "receive_in_app": self.receive_in_app,
            "receive_push": self.receive_push,
            "receive_sms": self.receive_sms,
            "source": self.__class__.__name__
        }
    
class NotificationPreferenceProfile(models.Model):
    """
    Represents a set of notification preferences that can be applied to users.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=False)
    in_app_enabled = models.BooleanField(default=True)

    dnd_enabled = models.BooleanField(default=False)  # Do-not-disturb
    dnd_start_hour = models.PositiveSmallIntegerField(default=0)  # 0–23
    dnd_end_hour = models.PositiveSmallIntegerField(default=0)

    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Notification Preference Profile"
        verbose_name_plural = "Notification Preference Profiles"

    def __str__(self):
        return self.name
    

class EventNotificationPreference(models.Model):
    """
    A model that manages the events users want to receive notifications for.
    This allows users to enable/disable notifications for specific events.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="event_preferences"
    )
    website = models.ForeignKey(
        "websites.Website", null=True, blank=True, on_delete=models.CASCADE
    )
    event = models.CharField(max_length=100, choices=EventType.choices())
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)

    dnd_enabled = models.BooleanField(default=False)
    dnd_start = models.PositiveIntegerField(default=22)  # 10pm
    dnd_end = models.PositiveIntegerField(default=6)     # 6am


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "event")

class RoleNotificationPreference(models.Model):
    """
    Represents default notification preferences for a role.
    This allows roles to have a set of default notification preferences that can be applied to users.
    """
    role = models.OneToOneField(
        UserRole, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    
    default_channels = models.JSONField(default=list)  # e.g., ['email', 'in_app']
    min_priority = models.PositiveSmallIntegerField(default=NotificationPriority.NORMAL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("role", "website")

    def __str__(self):
        return f"{self.role.name} Defaults @ {self.website.domain}"


    
class ChannelPreference(models.Model):
    """ Represents a user's preference for a specific notification channel.
    This allows users to enable/disable specific channels for notifications.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="channel_preferences"
    )
    user_pref = models.ForeignKey(
        UserNotificationPreference, on_delete=models.CASCADE,
        related_name="channel_prefs"
    )
    channel = models.CharField(
        max_length=32, choices=NotificationType.choices()
    )
    no_notify = models.BooleanField(default=False)
    digest_only = models.BooleanField(default=False)

    def __str__(self):
        return f"Channel Preference for {self.user_pref.user} - {self.channel}"
    
    class Meta:
        unique_together = ('website', 'user_pref', 'channel')
        verbose_name = "Channel Preference"
        verbose_name_plural = "Channel Preferences"