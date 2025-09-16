import logging
import time
from datetime import timedelta
from notifications_system.enums import NotificationChannel
from notifications_system.services.delivery import NotificationDeliveryService
from notifications_system.services.preferences import NotificationPreferenceResolver
from django.utils import timezone

logger = logging.getLogger(__name__)


class FallbackOrchestrator:
    """
    Orchestrates fallback delivery when the preferred channel fails.
    Supports dynamic event-based fallback routing, retry delay (e.g., exponential backoff),
    and respects user preferences.
    """

    def __init__(self, notification, *, tried_channels=None, max_retries=3):
        self.notification = notification
        self.user = notification.user
        self.event = notification.event
        self.tried_channels = tried_channels or set()
        self.max_retries = max_retries
        self.retry_count = 0

        self.channel_pipeline = self._build_fallback_pipeline()

    def _build_fallback_pipeline(self):
        """
        Build a channel preference fallback pipeline:
        - Respects user's notification preferences (if any)
        - Supports event-based overrides
        - Falls back to default pipeline
        """
        try:
            prefs = NotificationPreferenceResolver.get_user_channel_order(self.user, self.event)
            logger.debug(f"[Fallback] User channel prefs for {self.user}: {prefs}")
            return prefs or self._default_fallback_order()
        except Exception as e:
            logger.warning(f"[Fallback] Preference load failed: {e}")
            return self._default_fallback_order()

    def _default_fallback_order(self):
        """
        Default fallback order. You can override this by event type or criticality.
        """
        return [
            NotificationChannel.PUSH,
            NotificationChannel.IN_APP,
            NotificationChannel.WEBSOCKET,
            NotificationChannel.EMAIL,
            NotificationChannel.SMS,
            NotificationChannel.TELEGRAM,
        ]

    def _retry_delay(self, attempt):
        """
        Use exponential backoff with jitter.
        """
        base = 2 ** attempt
        jitter = 0.5 + (attempt * 0.1)
        return base + jitter

    def get_next_channel(self):
        for channel in self.channel_pipeline:
            if channel not in self.tried_channels:
                return channel
        return None

    def run(self, *, async_mode=False):
        """
        Run fallback orchestration.
        If async_mode=True, handle backoff with Celery instead of blocking.
        """
        while self.retry_count < self.max_retries:
            next_channel = self.get_next_channel()
            if not next_channel:
                logger.warning(
                    f"[Fallback] No more channels to try for notification {self.notification.id}"
                )
                return False

            logger.info(
                f"[Fallback] Trying channel={next_channel} (attempt={self.retry_count + 1})"
            )
            self.tried_channels.add(next_channel)

            try:
                success = NotificationDeliveryService.deliver(self.notification, channel=next_channel)
            except Exception as e:
                logger.error(
                    f"[Fallback] Delivery exception on {next_channel}: {e}", exc_info=True
                )
                success = False

            if success:
                logger.info(
                    f"[Fallback] Notification {self.notification.id} delivered via {next_channel}"
                )
                return True

            self.retry_count += 1

            if async_mode:
                # Defer to Celery retry mechanism or requeue the task later
                logger.info(
                    f"[Fallback] Async retry requested, stopping at attempt {self.retry_count}"
                )
                return False

            delay = self._retry_delay(self.retry_count)
            logger.info(
                f"[Fallback] Waiting {delay:.2f}s before next fallback attempt..."
            )
            time.sleep(delay)

        logger.warning(
            f"[Fallback] Max retries exhausted for notification {self.notification.id}"
        )
        return False

    def _handle_fallbacks(self, notification, channel, html_message=None, email_override=None):
        """
        Handle fallback delivery for notifications.
        """
        FallbackOrchestrator(notification, channel, html_message=html_message,
                             email_override=email_override).run()


# """
# A module to handle fallback notification logic
# for users based on their notification profiles.
# This includes managing fallback channels, retry logic,
# and ensuring notifications are sent according to user preferences.
# It integrates with the notification system settings
# and user profiles to determine the best delivery method.
# """
# import logging
# from activity.services import logger
# from notifications_system.models.notification_settings import (
#     NotificationSystemSettings
# )
# from datetime import timedelta
# from django.utils import timezone
# from authentication.models import UserSession
# from notifications_system.models.notification_group import NotificationGroup
# from notifications_system.models.notification_profile import (
#     GroupNotificationProfile
# )
# from notifications_system.utils.email_helpers import send_website_mail
# from notifications_system.utils.sms_helpers import send_sms_notification
# from notifications_system.utils.push_helpers import send_push_notification
# from notifications_system.utils.in_app_helpers import send_in_app_notification
# from notifications_system.utils.ws_helpers import send_ws_notification

# from django.conf import settings
# from users.models import User


# logger = logging.getLogger(__name__)

# INACTIVITY_HOURS = getattr(settings, "NOTIFY_INACTIVITY_FALLBACK_HOURS", 3)
# EMAIL_COOLDOWN_MINUTES = getattr(settings, "NOTIFY_EMAIL_COOLDOWN_MINUTES", 30)
# DAILY_FALLBACK_LIMIT = getattr(settings, "NOTIFY_DAILY_EMAIL_LIMIT", 5)
# WEEKLY_FALLBACK_LIMIT = getattr(settings, "NOTIFY_WEEKLY_EMAIL_LIMIT", 20)
# GLOBAL_DISABLE_EMAIL_FALLBACK = getattr(settings, "NOTIFY_DISABLE_EMAIL_FALLBACK", False)


# def get_fallback_chain(profile, channel):
#     rules = (getattr(profile, "fallback_rules", None) or 
#              NotificationSystemSettings.get_solo().fallback_rules or {})
#     return rules.get(channel, [])

# def get_max_retries(profile, channel):
#     retries = (getattr(profile, "max_retries_per_channel", None) or 
#                NotificationSystemSettings.get_solo().max_retries_per_channel or {})
#     return retries.get(channel, 1)

# def mark_email_fallback_sent(user, group):
#     try:
#         profile = GroupNotificationProfile.objects.get(user=user, group=group)
#         profile.last_email_notification_at = timezone.now()
#         profile.save(update_fields=["last_email_notification_at"])
#     except GroupNotificationProfile.DoesNotExist:
#         pass

# def dispatch_notification(user, event, payload, primary_channels):
#     attempted = set()

#     for channel in primary_channels:
#         success = try_send_channel(user, channel, payload)
#         attempted.add(channel)

#         if not success:
#             fallback_chain = get_fallback_chain(
#                 user.notification_profile, channel
#             )
#             for fallback in fallback_chain:
#                 if fallback in attempted:
#                     continue  # avoid retry loops
#                 success = try_send_channel(user, fallback, payload)
#                 attempted.add(fallback)
#                 if success:
#                     break


# def try_send_channel(user, channel, payload):
#     try:
#         if channel == "email":
#             return send_website_mail(user, payload)
#         elif channel == "sms":
#             return send_sms_notification(user, payload)
#         elif channel == "push":
#             return send_push_notification(user, payload)
#         elif channel == "in_app":
#             return send_in_app_notification(user, payload)
#         elif channel == "websocket":
#             return send_ws_notification(user, payload)
#     except Exception as e:
#         logger.warning(f"Failed {channel} for {user}: {e}")
#     return False

# def max_retries_per_channel():
#     """Returns the maximum number of retries allowed per channel."""
#     return {
#         "email": 3,
#         "sms": 3,
#         "push": 3,
#         "in_app": 5,
#         "websocket": 5,
#     }

# def should_fall_back_to_email(user: User, group: NotificationGroup = None) -> bool:
#     now = timezone.now()

#     if GLOBAL_DISABLE_EMAIL_FALLBACK:
#         logger.info(f"Global email fallback disabled — skipping for user {user.id}")
#         return False

#     if getattr(user, "disable_email_fallback", False):
#         logger.info(f"User {user.id} has disabled email fallbacks")
#         return False

#     if group:
#         try:
#             profile = GroupNotificationProfile.objects.get(user=user, group=group)

#             if not profile.allow_email_fallback:
#                 logger.info(f"User {user.id} opted out of email fallback for group {group.slug}")
#                 return False

#             if profile.last_email_notification_at and profile.last_email_notification_at > now - timedelta(minutes=EMAIL_COOLDOWN_MINUTES):
#                 logger.info(f"Email fallback cooldown active for user {user.id} in group {group.slug}")
#                 return False
#         except GroupNotificationProfile.DoesNotExist:
#             logger.warning(f"No profile found for user {user.id} in group {group.slug}, assuming fallback allowed")

#     # Rate-limit daily/weekly emails
#     if exceeded_email_rate_limit(user):
#         logger.info(f"User {user.id} exceeded fallback rate limit")
#         return False

#     # Inactivity check
#     threshold = now - timedelta(hours=INACTIVITY_HOURS)
#     session = (
#         UserSession.objects.filter(user=user)
#         .order_by("-last_activity")
#         .first()
#     )

#     if not session or session.last_activity < threshold:
#         logger.info(f"User {user.id} inactive — triggering email fallback")
#         return True

#     return False


# def exceeded_email_rate_limit(user: User) -> bool:
#     from notifications_system.models.notification_log import EmailNotificationLog  # optional table

#     now = timezone.now()
#     today = now.date()
#     week_start = today - timedelta(days=today.weekday())

#     daily_count = EmailNotificationLog.objects.filter(
#         user=user, created_at__date=today
#     ).count()
#     weekly_count = EmailNotificationLog.objects.filter(
#         user=user, created_at__date__gte=week_start
#     ).count()

#     return daily_count >= DAILY_FALLBACK_LIMIT or weekly_count >= WEEKLY_FALLBACK_LIMIT


# def mark_email_fallback_sent(user: User, group: NotificationGroup = None):
#     from notifications_system.models.notification_profile import (
#         GroupNotificationProfile
#     )
#     from notifications_system.models.notification_log import EmailNotificationLog

#     if group:
#         try:
#             profile = GroupNotificationProfile.objects.get(
#                 user=user, group=group
#             )
#             profile.last_email_notification_at = timezone.now()
#             profile.save(update_fields=["last_email_notification_at"])
#         except GroupNotificationProfile.DoesNotExist:
#             pass

#     # Save a log to track rate limits
#     EmailNotificationLog.objects.create(user=user, group=group)