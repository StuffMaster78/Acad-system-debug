"""Resolvers for notification preferences, profiles, and channels."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from django.db import models

from notifications_system.enums import NotificationType
from notifications_system.models.notification_preferences import (
    EventNotificationPreference,
    NotificationPreference,
    RoleNotificationPreference,
)
from notifications_system.models.notification_profile import (
    NotificationGroupProfile,
    NotificationProfile,
)


_CHANNEL_FLAG_MAP: Dict[str, str] = {
    NotificationType.EMAIL: "email_enabled",
    NotificationType.SMS: "sms_enabled",
    NotificationType.PUSH: "push_enabled",
    NotificationType.WEBHOOK: "webhook_enabled",
    NotificationType.TELEGRAM: "telegram_enabled",
    NotificationType.DISCORD: "discord_enabled",
    NotificationType.IN_APP: "in_app_enabled",
}


def resolve_channel_preferences(user) -> Optional[Dict[str, object]]:
    """Resolve a user's effective on/off flags for each channel.

    Looks up the user's `NotificationPreference` and attached profile.
    Returns a dict of booleans (plus DND window) or None if nothing found.

    Args:
        user: Authenticated user.

    Returns:
        Dict of flags like ``{"email": True, "sms": False, ...}`` or None.
    """
    pref = NotificationPreference.objects.filter(user=user).select_related(
        "profile"
    ).first()
    if not pref or not pref.profile:
        return None

    p = pref.profile
    return {
        "email": p.email_enabled,
        "sms": p.sms_enabled,
        "push": p.push_enabled,
        "webhook": p.webhook_enabled,
        "telegram": p.telegram_enabled,
        "discord": p.discord_enabled,
        "in_app": p.in_app_enabled,
        "dnd_enabled": p.dnd_enabled,
        "dnd_start": p.dnd_start_hour,
        "dnd_end": p.dnd_end_hour,
    }


def resolve_group_profile(user, website) -> Optional[NotificationGroupProfile]:
    """Return the first active group profile applicable to the user.

    Args:
        user: Authenticated user.
        website: Current tenant/website.

    Returns:
        A ``NotificationGroupProfile`` or None.
    """
    return (
        NotificationGroupProfile.objects.filter(
            website=website,
            is_active=True,
        )
        .filter(models.Q(users=user) | models.Q(roles__in=user.roles.all()))
        .first()
    )


def resolve_role_default(
    user, website
) -> Optional[RoleNotificationPreference]:
    """Return role default preferences for the user if available.

    Args:
        user: Authenticated user expected to have ``role``.
        website: Current tenant/website.

    Returns:
        A ``RoleNotificationPreference`` or None.
    """
    if not hasattr(user, "role"):
        return None
    try:
        return RoleNotificationPreference.objects.get(
            role=user.role,
            website=website,
        )
    except RoleNotificationPreference.DoesNotExist:
        return None


def _flag_enabled(pref_obj, channel: str) -> bool:
    """Generic check: does ``pref_obj`` enable a given channel?

    Args:
        pref_obj: Object with boolean fields like ``email_enabled``.
        channel: One of ``NotificationType`` values.

    Returns:
        True if enabled, else False.
    """
    flag_name = _CHANNEL_FLAG_MAP.get(channel)
    if not flag_name:
        return False
    return bool(getattr(pref_obj, flag_name, False))


def get_user_notification_channels(
    user,
    event,
    website,
    requested_channels: Iterable[str],
) -> List[str]:
    """Filter requested channels by user/event/website preferences.

    Preference resolution order per channel:
        1. Event-specific override (exact website, then global event pref)
        2. General user preferences
        3. (If neither exists) channel is rejected

    Args:
        user: Target user.
        event: Event instance or key used by EventNotificationPreference.
        website: Tenant/website.
        requested_channels: Channels proposed by caller.

    Returns:
        List of channels allowed for delivery.
    """
    event_pref = (
        EventNotificationPreference.objects.filter(
            user=user,
            event=event,
            website=website,
        ).first()
        or EventNotificationPreference.objects.filter(
            user=user,
            event=event,
            website__isnull=True,
        ).first()
    )

    general_pref = NotificationPreference.objects.filter(user=user).first()

    allowed: List[str] = []
    for channel in requested_channels:
        if event_pref and _flag_enabled(event_pref, channel):
            allowed.append(channel)
            continue

        if not event_pref and general_pref and _flag_enabled(
            general_pref, channel
        ):
            allowed.append(channel)
            continue

        # No explicit opt-in: reject channel.
    return allowed


def resolve_profile_settings(user):
    """Resolve the effective profile-like settings object for a user.

    The lookup sequence is:
        1) User-specific NotificationProfile on this website
        2) Group profile on this website
        3) Role-level default preference
        4) None

    Args:
        user: Authenticated user expected to carry a ``website`` attr.

    Returns:
        A profile/preference-like object or None.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return None

    website = getattr(user, "website", None)

    # 1) User-specific profile
    profile = NotificationProfile.objects.filter(
        user=user,
        website=website,
    ).first()
    if profile:
        return profile

    # 2) Group profile
    profile = resolve_group_profile(user, website)
    if profile:
        return profile

    # 3) Role default
    return resolve_role_default(user, website)