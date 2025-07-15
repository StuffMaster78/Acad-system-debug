from turtle import update
from django.utils import timezone
from django.conf import settings
from notifications_system.models import (
    Notification,
    NotificationPreference,
    NotificationDelivery,
    NotificationLog
)
from notifications_system.notification_enums import (
    NotificationType,
    DeliveryStatus
)
from notifications_system.services.templates_registry import get_template

from core.utils.email_helpers import send_website_mail
from core.utils.sms_helpers import send_sms_notification
from core.utils.push_helpers import send_push_notification
from core.utils.ws_helpers import send_ws_notification
from notifications_system.utils.priority_mapper import get_priority_from_label
from notifications_system.notification_enums import NotificationPriority

import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """A centralized Service for managing and delivering notifications to users."""
    @staticmethod
    def send(
        *,
        user,
        event,
        context=None,
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
        """
        Create and deliver a notification across selected channels.
        """

        if not user:
            logger.warning("Notification skipped: No user provided.")
            return None

        context = context or {}
        if priority_label:
            resolved_priority = get_priority_from_label(priority_label)
            if resolved_priority != priority:
                priority = resolved_priority


        preferences = getattr(user, "notification_preferences", None)

        if not channels:
            if preferences:
                channels = preferences.get_active_channels()
            else:
                channels = [NotificationType.IN_APP]

        # Fetch and render templates
        template = get_template(event)
        if not template:
            logger.warning(f"No template registered for event '{event}'")
            return None

        title, message, html = template.render(context)

        # Create a DB notification record
        notification = Notification.objects.create(
            user=user,
            actor=actor,
            event=event,
            payload=context,
            website=website,
            type=channels[0],  # primary channel
            title=title,
            message=message,
            rendered_title=title,
            rendered_message=message,
            rendered_link=context.get("link"),
            rendered_payload=context,
            template_name=template_name or template.event_name,
            template_version=context.get("version"),
            category=category or "info",
            priority=priority,
            is_critical=is_critical,
            is_digest=is_digest,
            digest_group=digest_group,
            is_silent=is_silent,
            status=DeliveryStatus.PENDING,
        )

        if is_silent:
            return notification  # skip delivery

        for channel in channels:
            # Skip disabled channels
            if preferences and not NotificationService._is_channel_enabled(
                preferences, channel
            ):
                continue
            try:
                NotificationService._deliver(
                    notification,
                    channel,
                    html_message=html,
                    email_override=email_override
                )

            except Exception as e:
                logger.error(f"[{channel}] delivery failed for {user}: {e}", exc_info=True)
                NotificationDelivery.objects.create(
                    notification=notification,
                    channel=channel,
                    status=DeliveryStatus.FAILED,
                    error_message=str(e),
                    attempts=1
                )

        # Final update
        notification.status = DeliveryStatus.SENT
        notification.sent_at = timezone.now()
        notification.save()

        return notification
    
    @staticmethod
    def _is_channel_enabled(preferences, channel):
        return {
            NotificationType.EMAIL: preferences.receive_email,
            NotificationType.SMS: preferences.receive_sms,
            NotificationType.PUSH: preferences.receive_push,
            NotificationType.IN_APP: preferences.receive_in_app,
        }.get(channel, True)

    @staticmethod
    def _deliver(
        notification,
        channel,
        html_message=None,
        email_override=None
    ):
        """
        Perform actual delivery to the given channel.
        """
        user = notification.user
        message = notification.message
        title = notification.title

        if channel == NotificationType.EMAIL:
            send_website_mail(
                subject=title,
                message=message,
                html_message=html_message,
                recipient_list=[email_override or user.email],
                tenant=notification.website
            )

        elif channel == NotificationType.SMS:
            send_sms_notification(user, message)

        elif channel == NotificationType.PUSH:
            send_push_notification(user, message)

        elif channel == NotificationType.IN_APP:
            send_ws_notification(user, message)

        else:
            raise ValueError(f"Unsupported channel: {channel}")

        NotificationDelivery.objects.create(
            notification=notification,
            channel=channel,
            status=DeliveryStatus.SENT,
            sent_at=timezone.now(),
            attempts=1
        )

        NotificationLog.objects.create(
            notification=notification,
            channel=channel,
            success=True,
            response_code=200,
            response_message="Notification sent successfully",
            status=DeliveryStatus.SENT,
            message=f"Notification sent via {channel} to {user.username}",
            timestamp=timezone.now()
        )

        # if success:
        #     notification.status = DeliveryStatus.SENT
        #     notification.sent_at = timezone.now()
        # else:
        #     notification.status = DeliveryStatus.FAILED
        #     notification.error_message = "Delivery failed"
        #     notification.save() 
        
        # notification.save(update_fields=['status', 'sent_at'])

        # return success