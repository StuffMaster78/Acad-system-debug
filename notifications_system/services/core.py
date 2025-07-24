import time
from turtle import update
from typing import override
from django.utils import timezone
from django.conf import settings
from notifications_system.models.notifications import (
    Notification
)
from notifications_system.models.broadcast_notification import (
    BroadcastNotification,
    BroadcastOverride
)
from notifications_system.models.notification_delivery import (
    NotificationDelivery
)
from notifications_system.models.digest_notifications import (
    NotificationDigest
)
from notifications_system.models.notification_log import (
    NotificationLog
)
from notifications_system.enums import (
    NotificationType,
    DeliveryStatus
)
from notifications_system.services.dispatch import NotificationDispatcher
from notifications_system.services.templates_registry import get_template

from notifications_system.utils.email_helpers import send_website_mail
from notifications_system.utils.sms_helpers import send_sms_notification
from notifications_system.utils.push_helpers import send_push_notification
from notifications_system.utils.ws_helpers import send_ws_notification
from notifications_system.utils.priority_mapper import get_priority_from_label
from notifications_system.utils.retry_task import retry_task_with_backoff
from notifications_system.enums import NotificationPriority
from notifications_system.delivery import CHANNEL_BACKENDS
from notifications_system.utils.dnd import is_dnd_now
from notifications_system.utils.email_renderer import render_notification_email
from notifications_system.utils.filter_preferred_channels import filter_channels_by_user_preferences
from notifications_system.services.preferences import get_target_users
import logging
from notifications_system.models import EventNotificationPreference
from django.db import models

from notifications_system.utils.fallbacks import should_fall_back_to_email, mark_email_fallback_sent
from notifications_system.utils.dnd import is_dnd_now
from notifications_system.services.preferences import NotificationPreferenceResolver

logger = logging.getLogger(__name__)


class NotificationService:
    """
    A centralized Service for managing and delivering notifications to users.
    This service handles the creation, delivery, and management of notifications.
    """
    @staticmethod
    def send_notification(
        *,
        user,
        event,
        payload=None,
        website=None,
        actor=None,
        channels=None,
        category=None,
        template_name=None,
        priority=5,
        priority_label=None,
        is_critical=False,
        is_digest=False,
        digest_group=None,
        is_silent=False,
        email_override=None,
    ):
        # Validate user
        if not user or not user.is_authenticated:
            logger.warning("Notification skipped: Invalid user.")
            return None

        # Validate event
        if not event:
            logger.warning("Notification skipped: Invalid event.")
            return None
        
        # Validate website
        if not website:
            logger.warning("Notification skipped: No website provided.")
            return None
        # Validate payload
        if not payload:
            logger.warning("Notification skipped: No payload provided.")
            return None     
        payload = payload or {}

        # Check if user has notification profile
        if not hasattr(user, 'notification_profile'):
            logger.warning(
                f"User {user} has no notification profile. Skipping notification."
            )
            return None
        
        # Check if user has notification preferences
        if not hasattr(user, 'notification_preferences'):
            logger.warning(
                f"User {user} has no notification preferences. Assigning defaults."
            )
            NotificationPreferenceResolver.assign_default_preferences(user)

        # Check if user is muted
        if user.pref.is_muted() and not is_critical:
            logger.info(f"User {user} is muted. Skipping notification.")
            return None
        
        # Check if user is in DND hours
        if is_dnd_now(user.notification_profile):
            channels = [ch for ch in (channels or []) if ch not in user.notification_profile.dnd_channels]
            if not channels:
                logger.info(
                    f"User {user} is in DND hours. Skipping notification."
                )
                return None
            
        # Filter channels based on user preferences
        if channels:
            channels = filter_channels_by_user_preferences(
                user=user,
                channels=channels,
                website=website
            )
        else:
            channels = NotificationPreferenceResolver.get_effective_preferences(
                user=user, website=website
            )

        # Priority handling
        if isinstance(priority, str):
            priority = get_priority_from_label(priority) or NotificationPriority.NORMAL 
        if priority is None:
            priority = NotificationPriority.NORMAL

        # Handle Broadcasts
        if (broadcast := BroadcastNotification.objects.filter(event_type=event, is_active=True).first()):
            users = get_target_users(broadcast)
            NotificationDispatcher.dispatch(
                users, subject=broadcast.title, message=broadcast.message,
                website=website, event=event, payload=payload, channels=channels,
                category=category, priority=priority, is_critical=is_critical,
                is_digest=is_digest, digest_group=digest_group, is_silent=is_silent,
                email_override=email_override
            )
            return broadcast

        
        # Handle Broadcast Overrides
        payload = payload.copy()
        payload["user_id"] = user.id
        payload["website_id"] = website.id if website else None

        if (override := BroadcastOverride.objects.filter(event_type=event, active=True).first()):
            payload["title"] = override.title
            payload["message"] = override.message
            channels = override.force_channels


        # Handle Digests
        profile = getattr(user, "notification_profile", None)
        preferences = getattr(user, "notification_preferences", None)

        if is_digest and profile and preferences:
            digest_group = f"{event}_{user.id}"
            payload["digest_group"] = digest_group
            payload["is_digest"] = True

        # Default to IN_APP
        if not channels:
            channels = NotificationPreferenceResolver.get_effective_preferences(
                user=user, website=website
            ) if preferences else [NotificationType.IN_APP]

        # Template rendering
        template = get_template(event)
        if not template:
            logger.warning(f"No template registered for event '{event}'")
            return None

        title, message, html = template.render(payload)


        # Create DB notification
        notification = Notification.objects.create(
            user=user,
            actor=actor,
            event=event,
            payload=payload,
            website=website,
            type=channels[0],
            title=title,
            message=message,
            rendered_title=title,
            rendered_message=message,
            rendered_link=payload.get("link"),
            rendered_payload=payload,
            template_name=template_name or template.event_name,
            template_version=payload.get("version"),
            category=category or "info",
            priority=priority,
            is_critical=is_critical,
            is_digest=is_digest,
            digest_group=digest_group,
            is_silent=is_silent,
            status=DeliveryStatus.PENDING,
        )

        if is_silent:
            return notification

        for channel in channels:
            if not NotificationService._is_channel_enabled(user, preferences, channel):
                continue

            try:
                NotificationService._deliver(
                    notification, channel,
                    html_message=html,
                    email_override=email_override
                )
            except Exception as e:
                logger.exception(f"[{channel}] delivery failed for {user}: {e}")
                NotificationDelivery.objects.create(
                    notification=notification,
                    channel=channel,
                    status=DeliveryStatus.FAILED,
                    error_message=str(e),
                    attempts=1
                )

        # Log Notification
        NotificationLog.objects.create(
            notification=notification,
            channel=channels,
            success=True,
            response_code=200,
            status=DeliveryStatus.SENT,
            message=f"Notification sent via {', '.join(channels)}",
            timestamp=timezone.now()
        )
        logger.info(
            f"Notification sent to {user} via {', '.join(channels)} for event '{event}'"
        )
        # Update notification status
        notification.status = DeliveryStatus.SENT
        notification.sent_at = timezone.now()
        notification.save()

        return notification

    @staticmethod
    def _is_channel_enabled(user, preferences, channel):
        if not preferences:
            return True
        if channel == NotificationType.EMAIL:
            return preferences.receive_email
        if channel == NotificationType.SMS:
            return preferences.receive_sms
        if channel == NotificationType.PUSH:
            return preferences.receive_push
        if channel == NotificationType.IN_APP:
            return preferences.receive_in_app

        return True


    @staticmethod
    def _deliver(notification, channel, html_message=None, email_override=None, attempt=1):
        backend_cls = CHANNEL_BACKENDS.get(channel)
        if not backend_cls:
            raise ValueError(f"Unsupported delivery channel: {channel}")

        backend = backend_cls(notification, channel_config={
            "html_message": html_message,
            "email_override": email_override
        })

        try:
            success = backend.send()
        except Exception as e:
            success = False
            logger.exception(f"[{channel}] Error during delivery: {e}")

        NotificationDelivery.objects.create(
            notification=notification,
            channel=channel,
            status=DeliveryStatus.SENT if success else DeliveryStatus.FAILED,
            sent_at=timezone.now(),
            attempts=attempt
        )

        NotificationLog.objects.create(
            notification=notification,
            channel=channel,
            success=success,
            response_code=200 if success else 500,
            status=DeliveryStatus.SENT if success else DeliveryStatus.FAILED,
            message=f"[{channel.upper()}] Attempt {attempt}: {'Success' if success else 'Failure'}",
            timestamp=timezone.now()
        )

        if not success and attempt < settings.DEFAULT_MAX_RETRIES:
            time.sleep(settings.CHANNEL_BACKOFFS.get(channel, 10))
            return NotificationService._deliver(
                notification, channel, html_message=html_message,
                email_override=email_override, attempt=attempt + 1
            )

        if not success:
            for fallback in settings.CHANNEL_FALLBACKS.get(channel, []):
                if should_fall_back_to_email(notification.user, group=notification.group):
                    NotificationService._deliver(
                        notification, fallback,
                        html_message=html_message,
                        email_override=email_override
                    )
                    mark_email_fallback_sent(notification.user, notification.group)


    @staticmethod
    def send_broadcast(
        event, title, message, context=None, website=None,
        channels=None, priority=NotificationPriority.NORMAL
    ):
        channels = channels or [NotificationType.IN_APP, NotificationType.EMAIL]
        broadcast = BroadcastNotification.objects.create(
            event_type=event,
            title=title,
            message=message,
            context=context or {},
            website=website,
            priority=priority
        )
        for user in get_target_users(broadcast):
            NotificationService.send(
                user=user,
                event=event,
                context=context,
                website=website,
                channels=channels,
                is_critical=False
            )
        return broadcast

    @staticmethod
    def send_digests(group, since=None):
        digests = NotificationDigest.objects.filter(
            group=group,
            created_at__gte=since or timezone.now() - timezone.timedelta(days=1)
        )

        for digest in digests:
            for user in digest.users.all():
                NotificationService.send(
                    user=user,
                    event=digest.event,
                    context=digest.context,
                    website=digest.website,
                    channels=[NotificationType.EMAIL],
                    is_digest=True
                )
        return digests