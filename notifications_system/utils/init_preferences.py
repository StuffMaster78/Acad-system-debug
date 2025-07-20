from notifications_system.models.notification_profile import (
    NotificationProfile
)
from notifications_system.models.notification_preferences import (
    NotificationPreference
)
from django.contrib.auth.models import Group

def assign_default_profile(user):
    """Assigns a default notification preference
    profile to a user based on their role.
    If the user does not have a profile, it creates one
    with a default profile based on their role.
    """


    # Role-based defaults
    role_map = {
        "Writer": "Aggressive",
        "Client": "Minimal",
        "Support": "Balanced",
        "Editor": "Aggressive",
        "Admin": "Aggressive",
        "Superuser": "Aggressive",
    }

    default_profile = None

    # Role-based mapping
    for group_name, profile_name in role_map.items():
        if user.groups.filter(name=group_name).exists():
            default_profile = NotificationProfile.objects.filter(
                name=profile_name
            ).first()
            break

    # Fallback to global default
    if not default_profile:
        default_profile = NotificationProfile.objects.filter(
            name="Default"
        ).first()

    return NotificationPreference.objects.create(
        user=user,
        profile=default_profile,
        website=user.website
    )