from __future__ import annotations

from datetime import timedelta
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

from users.models.profile_reminder import (
    ProfileReminder,
    ProfileReminderStatus,
)
from users.models.user import User


def get_latest_reminder_for_user(
    *,
    user: User,
    reminder_type: str,
) -> ProfileReminder | None:
    """
    Return the latest reminder of a given type for a user.
    """
    return (
        ProfileReminder.objects.filter(
            user=user,
            reminder_type=reminder_type,
        )
        .order_by("-sent_at")
        .first()
    )


def has_recent_sent_reminder(
    *,
    user: User,
    reminder_type: str,
    cooldown_days: int,
) -> bool:
    """
    Return True if a successful reminder was sent within the cooldown window.
    """
    cutoff = timezone.now() - timedelta(days=cooldown_days)
    return ProfileReminder.objects.filter(
        user=user,
        reminder_type=reminder_type,
        status=ProfileReminderStatus.SENT,
        sent_at__gte=cutoff,
    ).exists()


def list_users_missing_phone() -> QuerySet[User]:
    """
    Return active users with no phone number and a valid website.
    """
    return User.objects.select_related("website", "profile").filter(
        is_active=True,
        website__isnull=False,
        phone_number="",
    )


def list_users_missing_phone_with_null() -> QuerySet[User]:
    """
    Return active users with missing phone number, including null or blank.
    """
    return User.objects.select_related("website", "profile").filter(
        is_active=True,
        website__isnull=False,
    ).filter(
        models.Q(phone_number="") | models.Q(phone_number__isnull=True)
    )