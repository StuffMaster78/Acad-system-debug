"""A function to filter notification channels based on user preferences.
This ensures that notifications are sent only through channels
that the user has opted into, enhancing user experience and compliance.
"""
from notifications_system.enums import NotificationType
from notifications_system.models.notification_preferences import (
    NotificationPreference
)

def filter_channels_by_user_preferences(user, requested_channels):
    """Filters the requested notification channels based on user preferences."""
    pref = NotificationPreference.objects.filter(user=user).first()
    if not pref:
        return requested_channels

    allowed = []
    for channel in requested_channels:
        if (
            (channel == NotificationType.EMAIL and pref.email_enabled) or
            (channel == NotificationType.SMS and pref.sms_enabled) or
            (channel == NotificationType.PUSH and pref.push_enabled) or
            (channel == NotificationType.IN_APP and pref.in_app_enabled) or
            (channel == NotificationType.WEBHOOK and pref.webhook_enabled) or
            (channel == NotificationType.SLACK and pref.slack_enabled) or
            (channel == NotificationType.DISCORD and pref.discord_enabled) or
            (channel == NotificationType.TELEGRAM and pref.telegram_enabled)
        ):
            allowed.append(channel)

    return allowed