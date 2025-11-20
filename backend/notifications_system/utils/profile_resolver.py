"""Helpers for assigning default notification profiles/groups by role."""

from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction

from notifications_system.models.notification_preferences import (
    NotificationPreferenceGroup,
    NotificationPreference,
)
from notifications_system.models.notification_profile import (
    NotificationProfile,
    NotificationGroupProfile,
)


User = get_user_model()


# Maps a user.role (lowercased) → canonical profile/group name
ROLE_PROFILE_MAP = {
    "writer": "Aggressive",
    "client": "Minimal",
    "editor": "Night Owl",
    "support": "Balanced",
    "admin": "Aggressive",
    "superuser": "Aggressive",
    "guest": "Passive",
    "default": "Default",
}


def _role_key(user) -> Optional[str]:
    """Return a normalized (lowercased) role key for a user.

    Args:
        user: Django User instance with an optional ``role`` attribute.

    Returns:
        Lowercased role string or None if not present.
    """
    role = getattr(user, "role", None)
    if not role:
        return None
    return str(role).strip().lower() or None


@transaction.atomic
def assign_default_group(user) -> Optional[NotificationPreference]:
    """Assign a default preference group to the user based on their role.

    If a matching group exists, create (or reuse) a NotificationPreference
    for the user pointing at that group.

    Args:
        user: Django User instance.

    Returns:
        The user's NotificationPreference if created/found; otherwise None.
    """
    role = _role_key(user)
    if not role:
        return None

    group_name = ROLE_PROFILE_MAP.get(role)
    if not group_name:
        return None

    group = NotificationPreferenceGroup.objects.filter(name=group_name).first()
    if not group:
        return None

    pref, _ = NotificationPreference.objects.get_or_create(
        user=user,
        defaults={"profile_group": group},
    )
    # If it existed but had no group, set it
    if pref.profile_group_id is None and group.id:
        pref.profile_group = group
        pref.save(update_fields=["profile_group"])
    return pref


@transaction.atomic
def assign_default_profile_for_role(user) -> Optional[NotificationProfile]:
    """Assign a default notification profile to the user based on role.

    Args:
        user: Django User instance.

    Returns:
        The assigned NotificationProfile, or None if no match found.
    """
    role = _role_key(user)
    if not role:
        return None

    profile_name = ROLE_PROFILE_MAP.get(role)
    if not profile_name:
        return None

    profile = NotificationProfile.objects.filter(name=profile_name).first()
    if not profile:
        return None

    user.notification_profile = profile
    user.save(update_fields=["notification_profile"])
    return profile


@transaction.atomic
def apply_default_notification_profile(
    user,
) -> Optional[NotificationProfile]:
    """Apply a default profile from group membership or global default.

    Resolution order:
      1) First matching NotificationGroupProfile for any user group.
      2) Global default NotificationProfile (is_default=True, is_active=True).

    Args:
        user: Django User instance.

    Returns:
        The applied NotificationProfile or None.
    """
    # Group-level profile
    group_ids = list(user.groups.values_list("id", flat=True))
    match = (
        NotificationGroupProfile.objects.filter(group__id__in=group_ids)
        .select_related("profile")
        .first()
    )
    if match and match.profile_id:
        user.notification_profile = match.profile
        user.save(update_fields=["notification_profile"])
        return match.profile

    # Global default
    default = (
        NotificationProfile.objects.filter(name="Default", is_active=True)
        .first()
    )
    if default:
        user.notification_profile = default
        user.save(update_fields=["notification_profile"])
        return default

    return None