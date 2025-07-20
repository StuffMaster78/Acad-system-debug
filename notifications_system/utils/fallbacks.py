"""
A module to handle fallback notification logic
for users based on their notification profiles.
This includes managing fallback channels, retry logic,
and ensuring notifications are sent according to user preferences.
It integrates with the notification system settings
and user profiles to determine the best delivery method.
"""
import logging
from activity.services import logger
from notifications_system.models.notification_settings import (
    NotificationSystemSettings
)
from notifications_system.utils.email_helpers import send_website_mail
from notifications_system.utils.email_renderer import render_notification_email
from notifications_system.utils.profile_resolver import apply_default_notification_profile
from notifications_system.utils.send_website_mail import send_rich_notification_email
from datetime import timedelta
from django.utils import timezone
from authentication.models import UserSession
from notifications_system.models.notification_group import NotificationGroup
from notifications_system.models.notification_profile import (
    NotificationProfile,
    GroupNotificationProfile
)
from notifications_system.models.notification_preferences import (
    NotificationPreference,
    RoleNotificationPreference
)
# Import or define send_sms
from notifications_system.utils.send_notifications import (
    send_sms_notification,
    send_push_notification,
    send_in_app_notification,
    send_ws_notification
)
from django.conf import settings
from users.models import User


logger = logging.getLogger(__name__)

INACTIVITY_HOURS = getattr(settings, "NOTIFY_INACTIVITY_FALLBACK_HOURS", 3)
EMAIL_COOLDOWN_MINUTES = getattr(settings, "NOTIFY_EMAIL_COOLDOWN_MINUTES", 30)
DAILY_FALLBACK_LIMIT = getattr(settings, "NOTIFY_DAILY_EMAIL_LIMIT", 5)
WEEKLY_FALLBACK_LIMIT = getattr(settings, "NOTIFY_WEEKLY_EMAIL_LIMIT", 20)
GLOBAL_DISABLE_EMAIL_FALLBACK = getattr(settings, "NOTIFY_DISABLE_EMAIL_FALLBACK", False)


def get_fallback_chain(profile, channel):
    rules = (getattr(profile, "fallback_rules", None) or 
             NotificationSystemSettings.get_solo().fallback_rules or {})
    return rules.get(channel, [])

def get_max_retries(profile, channel):
    retries = (getattr(profile, "max_retries_per_channel", None) or 
               NotificationSystemSettings.get_solo().max_retries_per_channel or {})
    return retries.get(channel, 1)

def mark_email_fallback_sent(user, group):
    try:
        profile = GroupNotificationProfile.objects.get(user=user, group=group)
        profile.last_email_notification_at = timezone.now()
        profile.save(update_fields=["last_email_notification_at"])
    except GroupNotificationProfile.DoesNotExist:
        pass

def dispatch_notification(user, event, payload, primary_channels):
    attempted = set()

    for channel in primary_channels:
        success = try_send_channel(user, channel, payload)
        attempted.add(channel)

        if not success:
            fallback_chain = get_fallback_chain(
                user.notification_profile, channel
            )
            for fallback in fallback_chain:
                if fallback in attempted:
                    continue  # avoid retry loops
                success = try_send_channel(user, fallback, payload)
                attempted.add(fallback)
                if success:
                    break


def try_send_channel(user, channel, payload):
    try:
        if channel == "email":
            return send_website_mail(user, payload)
        elif channel == "sms":
            return send_sms_notification(user, payload)
        elif channel == "push":
            return send_push_notification(user, payload)
        elif channel == "in_app":
            return send_in_app_notification(user, payload)
        elif channel == "websocket":
            return send_ws_notification(user, payload)
    except Exception as e:
        logger.warning(f"Failed {channel} for {user}: {e}")
    return False

def max_retries_per_channel():
    """Returns the maximum number of retries allowed per channel."""
    return {
        "email": 3,
        "sms": 3,
        "push": 3,
        "in_app": 5,
        "websocket": 5,
    }

def should_fall_back_to_email(user: User, group: NotificationGroup = None) -> bool:
    now = timezone.now()

    if GLOBAL_DISABLE_EMAIL_FALLBACK:
        logger.info(f"Global email fallback disabled — skipping for user {user.id}")
        return False

    if getattr(user, "disable_email_fallback", False):
        logger.info(f"User {user.id} has disabled email fallbacks")
        return False

    if group:
        try:
            profile = GroupNotificationProfile.objects.get(user=user, group=group)

            if not profile.allow_email_fallback:
                logger.info(f"User {user.id} opted out of email fallback for group {group.slug}")
                return False

            if profile.last_email_notification_at and profile.last_email_notification_at > now - timedelta(minutes=EMAIL_COOLDOWN_MINUTES):
                logger.info(f"Email fallback cooldown active for user {user.id} in group {group.slug}")
                return False
        except GroupNotificationProfile.DoesNotExist:
            logger.warning(f"No profile found for user {user.id} in group {group.slug}, assuming fallback allowed")

    # Rate-limit daily/weekly emails
    if exceeded_email_rate_limit(user):
        logger.info(f"User {user.id} exceeded fallback rate limit")
        return False

    # Inactivity check
    threshold = now - timedelta(hours=INACTIVITY_HOURS)
    session = (
        UserSession.objects.filter(user=user)
        .order_by("-last_activity")
        .first()
    )

    if not session or session.last_activity < threshold:
        logger.info(f"User {user.id} inactive — triggering email fallback")
        return True

    return False


def exceeded_email_rate_limit(user: User) -> bool:
    from notifications_system.models.notification_log import EmailNotificationLog  # optional table

    now = timezone.now()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())

    daily_count = EmailNotificationLog.objects.filter(user=user, created_at__date=today).count()
    weekly_count = EmailNotificationLog.objects.filter(user=user, created_at__date__gte=week_start).count()

    return daily_count >= DAILY_FALLBACK_LIMIT or weekly_count >= WEEKLY_FALLBACK_LIMIT


def mark_email_fallback_sent(user: User, group: NotificationGroup = None):
    from notifications_system.models.notification_profile import GroupNotificationProfile
    from notifications_system.models.notification_log import EmailNotificationLog

    if group:
        try:
            profile = GroupNotificationProfile.objects.get(user=user, group=group)
            profile.last_email_notification_at = timezone.now()
            profile.save(update_fields=["last_email_notification_at"])
        except GroupNotificationProfile.DoesNotExist:
            pass

    # Save a log to track rate limits
    EmailNotificationLog.objects.create(user=user, group=group)