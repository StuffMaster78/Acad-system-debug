
from datetime import timezone
from django.db import models
from django.conf import settings
from notifications_system.enums import (
    NotificationType,
    NotificationPriority
)
from django.contrib.postgres.fields import ArrayField
from notifications_system.models.notifications import Notification
from users.mixins import UserRole   
from django.contrib.postgres.fields import JSONField
from notifications_system.models.notification_settings import  (
    GlobalNotificationSystemSettings
)
from notifications_system.models.notification_group import NotificationGroup

User = settings.AUTH_USER_MODEL


class NotificationProfile(models.Model):
    """
    Represents a notification profile that can be applied to users such as
    writers, clients, etc.
    This allows for user-specific notification settings.
    It can be used to define default notification preferences for users.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="notification_profiles",
        help_text="The user this profile belongs to."
    )
    website = models.ForeignKey("websites.Website", on_delete=models.CASCADE)

    name = models.CharField(max_length=64, unique=True, default="Custom")
    base_profile = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )
    description = models.TextField(blank=True)
    default_email = models.BooleanField(default=True)
    default_sms = models.BooleanField(default=False)
    default_push = models.BooleanField(default=False)
    default_in_app = models.BooleanField(default=True)
    dnd_start = models.TimeField(null=True, blank=True)
    dnd_end = models.TimeField(null=True, blank=True)
    dnd_channels = ArrayField(
        models.CharField(max_length=20),
        default=list, blank=True
    )
    fallback_rules = models.JSONField(default=dict, blank=True)
    max_retries_per_channel = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Notification Profile"
        verbose_name_plural = "Notification Profiles"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return super().__str__()
    
    def as_dict(self):
        return {
            "receive_email": self.receive_email,
            "receive_in_app": self.receive_in_app,
            "receive_push": self.receive_push,
            "receive_sms": self.receive_sms,
            "source": self.__class__.__name__
        }
    
    def get_fallback_rules(self):
        """Returns the fallback rules for this profile.
        If this profile has its own rules, return them.
        Otherwise, check the base profile or global settings.
        """
        if self.fallback_rules:
            return self.fallback_rules
        elif self.base_profile:
            return self.base_profile.get_fallback_rules()
        return GlobalNotificationSystemSettings.get_solo().fallback_rules or {}

    def get_max_retries(self):
        if self.max_retries_per_channel:
            return self.max_retries_per_channel
        elif self.base_profile:
            return self.base_profile.get_max_retries()
        return GlobalNotificationSystemSettings.get_solo().max_retries_per_channel or {}

    def get_retry_delay(attempt_number):
        return min(60 * attempt_number, 600)  # e.g. 1min, 2min, 3min… max 10min


class NotificationGroupProfile(models.Model):
    """
    Represents a notification profile that can be applied to groups.
    This allows for group-level notification settings.
    Can be used to define default notification preferences for groups such as
    writers, clients, etc.
    It can also be used to define notification preferences for specific user roles.
    """
    name = models.CharField(max_length=100)
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE
    )
    profile = models.ForeignKey(
        "notifications_system.NotificationProfile",
        on_delete=models.CASCADE
    )
    group = models.ForeignKey("auth.Group", on_delete=models.CASCADE)

    allowed_channels = models.JSONField(default=list)  # e.g., ["email", "in_app"]
    min_priority = models.PositiveSmallIntegerField(
        default=NotificationPriority.NORMAL
    )

    # Optional targeting
    roles = models.CharField(
            max_length=50,
            choices=[(role.name, role.value) for role in UserRole]
        )
    users = models.ManyToManyField(
        User, blank=True,
        help_text="Directly assigned users"
    )

    is_active = models.BooleanField(default=True)
    role_slug = models.SlugField(
        blank=True, null=True,
        help_text="Optional slug for the role (e.g., 'writer')"
    )

    is_default = models.BooleanField(default=False)

    # Delivery options
    receive_email = models.BooleanField(default=True)
    receive_in_app = models.BooleanField(default=True)
    receive_push = models.BooleanField(default=False)
    receive_sms = models.BooleanField(default=False)
    allowed_channels = models.JSONField(default=list)
    min_priority = models.PositiveSmallIntegerField(
        default=NotificationPriority.NORMAL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("website", "group")

    def __str__(self):
        return f"{self.name} ({self.website.domain})"
    
    def as_dict(self):
        return {
            "name": self.name,
            "website": self.website.domain,
            "profile": self.profile.name,
            "group": self.group.name,
            "allowed_channels": self.allowed_channels,
            "min_priority": self.min_priority,
            "roles": [role.name for role in self.roles.all()],
            "users": [user.username for user in self.users.all()],
            "is_active": self.is_active,
            "is_default": self.is_default,
            "receive_email": self.receive_email,
            "receive_in_app": self.receive_in_app,
            "receive_push": self.receive_push,
            "receive_sms": self.receive_sms,
            "role_slug": self.role_slug or "",
            "source": self.__class__.__name__,
        }
    def get_active_channels(self):
        return [
            channel for channel, enabled in {
                NotificationType.EMAIL: self.receive_email,
                NotificationType.IN_APP: self.receive_in_app,
                NotificationType.PUSH: self.receive_push,
                NotificationType.SMS: self.receive_sms,
            }.items() if enabled
        ]
    

class GroupNotificationProfile(models.Model):
    """
    Defines notification preferences for a user group or role, per website.
    """
    name = models.CharField(max_length=100)
    website = models.ForeignKey("websites.Website", on_delete=models.CASCADE)
    group = models.ForeignKey(NotificationGroup, on_delete=models.CASCADE)

    # Optional: if using a roles table instead of Django groups
    role_slug = models.SlugField(
        blank=True, null=True,
        help_text="Optional slug for the role (e.g., 'writer')"
    )

    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Delivery options
    receive_email = models.BooleanField(default=True)
    receive_in_app = models.BooleanField(default=True)
    receive_push = models.BooleanField(default=False)
    receive_sms = models.BooleanField(default=False)
    allowed_channels = models.JSONField(default=list)
    min_priority = models.PositiveSmallIntegerField(default=NotificationPriority.NORMAL)

    class Meta:
        unique_together = ("website", "group")

    def __str__(self):
        return f"{self.name} ({self.website.domain})"

    def get_active_channels(self):
        return [
            channel for channel, enabled in {
                NotificationType.EMAIL: self.receive_email,
                NotificationType.IN_APP: self.receive_in_app,
                NotificationType.PUSH: self.receive_push,
                NotificationType.SMS: self.receive_sms,
            }.items() if enabled
        ]