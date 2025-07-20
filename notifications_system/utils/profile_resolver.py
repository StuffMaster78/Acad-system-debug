from notifications_system.models.notification_preferences import (
    NotificationPreferenceGroup,
    NotificationPreference
)
from notifications_system.models.notification_profile import (
    NotificationProfile,
    NotificationGroupProfile
)

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

def assign_default_group(user):
    """
    Assigns a default notification preference group
    to a user based on their role.
    If the user has a role that matches a predefined group,
    it creates or retrieves a NotificationPreference
    for that user with the corresponding group.
    """
    group_name = ROLE_PROFILE_MAP.get(user.role)
    if group_name:
        group = NotificationPreferenceGroup.objects.filter(
            name=group_name
        ).first()
        NotificationPreference.objects.get_or_create(
            user=user,
            defaults={"profile_group": group}
        )


def assign_default_profile_for_role(user):
    """
    Assigns a default notification profile based on user role.
    This function checks the user's role and assigns
    a default notification profile accordingly.
    """
    role_defaults = {
        "writer": "Aggressive",
        "support": "Minimal",
        "editor": "Balanced",
        "client": "Night Owl",
        "admin": "Aggressive",
        "superuser": "Aggressive",
        "support": "Balanced",
        "default": "Default",
        "guest": "Passive",
    }
    profile_name = role_defaults.get(user.role)
    if profile_name:
        profile = NotificationProfile.objects.filter(
            name=profile_name
        ).first()
        if profile:
            user.notification_profile = profile
            user.save()


def apply_default_notification_profile(user):
    """ Applies the default notification profile
    based on the user's role and group memberships.
    This function first checks if the user has a specific
    notification profile assigned. If not, it checks
    the user's group memberships for a matching profile.
    If no profile is found, it falls back to the global default.
    """
    # Group-level profile
    group_ids = user.groups.values_list('id', flat=True)
    match = NotificationGroupProfile.objects.filter(
        group__id__in=group_ids
    ).first()

    if match:
        user.notification_profile = match.profile
        user.save(update_fields=["notification_profile"])
        return match.profile

    # Fallback to global default
    default = NotificationProfile.objects.filter(
        is_default=True, is_active=True
    ).first()
    if default:
        user.notification_profile = default
        user.save(update_fields=["notification_profile"])
        return default

    return None
