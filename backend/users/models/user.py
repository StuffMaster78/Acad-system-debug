from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from users.managers import ActiveManager, CustomUserManager
from users.mixins import (
    ApprovalMixin,
    DeletionMixin,
    DisciplineMixin,
    GeoDetectionMixin,
    ImpersonationMixin,
    LoginSecurityMixin,
    MFAMixin,
    NotificationPreferenceMixin,
    RoleMixin,
    SessionTrackingMixin,
    TimestampMixin,
    TrustedDeviceMixin,
    UserReferenceMixin,
)

if TYPE_CHECKING:
    from django.contrib.auth.models import UserManager


class User(  # pyright: ignore[reportIncompatibleVariableOverride]
    AbstractUser,
    PermissionsMixin,
    RoleMixin,
    MFAMixin,
    NotificationPreferenceMixin,
    LoginSecurityMixin,
    ImpersonationMixin,
    UserReferenceMixin,
    DeletionMixin,
    DisciplineMixin,
    GeoDetectionMixin,
    TimestampMixin,
    SessionTrackingMixin,
    TrustedDeviceMixin,
    ApprovalMixin,
):
    email = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)

    notification_profile = models.ForeignKey(
        "notifications_system.NotificationPreferenceProfile",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users",
    )

    is_available = models.BooleanField(default=True)

    website = models.ForeignKey(
        "websites.Website",
        related_name="website_users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = cast("UserManager[User]", CustomUserManager())
    active_users = ActiveManager()

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"