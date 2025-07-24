from notifications_system.models.notification_preferences import (
    NotificationPreference,
    RoleNotificationPreference,
    EventNotificationPreference
)
from notifications_system.models.notification_profile import (
    NotificationProfile,
    NotificationGroupProfile
)
from django.db import models
from notifications_system.enums import NotificationType


def resolve_channel_preferences(user):
    """ Resolve user's notification preferences for all channels."""
    user_pref = NotificationPreference.objects.filter(
        user=user
    ).first()
        
    if user_pref and user_pref.profile:
        profile = user_pref.profile
        return {
            "email": profile.email_enabled,
            "sms": profile.sms_enabled,
            "push": profile.push_enabled,
            "webhook": profile.webhook_enabled,
            "telegram": profile.telegram_enabled,
            "discord": profile.discord_enabled,
            "in_app": profile.in_app_enabled,
            "dnd_enabled": profile.dnd_enabled,
            "dnd_start": profile.dnd_start_hour,
            "dnd_end": profile.dnd_end_hour,
        }
        
def resolve_group_profile(user, website):
    profiles = NotificationGroupProfile.objects.filter(
        website=website, is_active=True
    ).filter(models.Q(users=user) | models.Q(roles__in=user.roles.all()))
        
    return profiles.first()  # Pick highest priority if multiple
        
def resolve_role_default(user, website):
    if not hasattr(user, "role"):
        return None

    try:
        return RoleNotificationPreference.objects.get(
            role=user.role, website=website
        )
    except RoleNotificationPreference.DoesNotExist:
        return None
    
def get_user_notification_channels(user, event, website, requested_channels):
    # Try specific override first
    event_pref = EventNotificationPreference.objects.filter(
        user=user,
        event=event,
        website=website
    ).first() or EventNotificationPreference.objects.filter(
        user=user,
        event=event,
        website__isnull=True
    ).first()

    general_pref = NotificationPreference.objects.filter(user=user).first()

    final_channels = []
    for channel in requested_channels:
        if channel == NotificationType.EMAIL:
            if event_pref and event_pref.email_enabled:
                final_channels.append(channel)
            elif not event_pref and general_pref and general_pref.email_enabled:
                final_channels.append(channel)
        # repeat for other channels...
    return final_channels


def resolve_profile_settings(user):
    """
    Resolve the notification profile settings for a user.
    This includes checking user preferences, group profiles, and role defaults.
    """
    if not user or not user.is_authenticated:
        return None

    website = user.website

    # Check user's notification profile
    profile = NotificationProfile.objects.filter(
        user=user, website=website
    ).first()
    
    if not profile:
        # Fallback to group profile if no user profile exists
        profile = resolve_group_profile(user, website)
    
    if not profile:
        # Fallback to role default preferences
        role_pref = resolve_role_default(user, website)
        if role_pref:
            return role_pref

    return profile