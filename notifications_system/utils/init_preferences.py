"""Defaults for user notification preferences."""

from __future__ import annotations

from typing import Optional

from django.contrib.auth.models import Group  # noqa: F401

from notifications_system.models.notification_preferences import (
    NotificationPreference,
)
from notifications_system.models.notification_profile import (
    NotificationProfile,
)


def assign_default_profile(user, website: Optional[object] = None
                           ) -> NotificationPreference:
    """Assign a default notification profile to a user.

    Chooses a profile based on the user's Django auth group membership
    (role). If no role match is found, uses the "Default" profile.
    The function is idempotent: if a preference already exists for the
    user+website, it returns it instead of creating a duplicate.

    Args:
        user: The user to initialize.
        website: Optional tenant/site object. Defaults to user.website.

    Returns:
        NotificationPreference: The existing or newly created preference.

    Raises:
        ValueError: If neither a role-based profile nor a global default
            profile is available in the database.
    """
    if not user:
        raise ValueError("assign_default_profile requires a user.")

    website = website or getattr(user, "website", None)

    # Return existing preference if present (idempotent).
    existing = NotificationPreference.objects.filter(
        user=user, website=website
    ).first()
    if existing:
        return existing

    # Role -> profile mapping.
    role_map = {
        "Writer": "Aggressive",
        "Client": "Minimal",
        "Support": "Balanced",
        "Editor": "Aggressive",
        "Admin": "Aggressive",
        "Superuser": "Aggressive",
    }

    profile = None
    for group_name, profile_name in role_map.items():
        if user.groups.filter(name=group_name).exists():
            profile = NotificationProfile.objects.filter(
                name=profile_name
            ).first()
            if profile:
                break

    # Fallback to global default profile.
    if not profile:
        profile = NotificationProfile.objects.filter(name="Default").first()

    if not profile:
        raise ValueError(
            "No suitable NotificationProfile found. Create a 'Default' "
            "profile or one of: Aggressive, Minimal, Balanced."
        )

    pref, _ = NotificationPreference.objects.get_or_create(
        user=user,
        website=website,
        defaults={"profile": profile},
    )
    # If it existed without a profile (edge case), set it now.
    if not getattr(pref, "profile", None):
        pref.profile = profile
        pref.save(update_fields=["profile"])

    return pref