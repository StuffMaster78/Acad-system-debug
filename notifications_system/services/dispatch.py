import logging
from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.template_engine import NotificationTemplateEngine
from notifications_system.registry.role_bindings import get_channels_for_role
from notifications_system.registry.template_registry import (
    NOTIFICATION_TEMPLATES,
    get_templates_for_event
)
from notifications_system.registry.forced_channels import FORCED_CHANNELS
from notifications_system.tasks import send_notification_task
from notifications_system.models.notifications import Notification
from django.core.mail import send_mail
from django.conf import settings
import requests  # type: ignore

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """
    Dispatches notifications across channels for a given user and event.
    Supports extensible backends.
    """

    def __init__(self, user, event_key: str, context: dict, role: str = None):
        self.user = user
        self.event_key = event_key
        self.context = context
        self.role = role or getattr(user, 'role', 'client')

    def dispatch(self):
        """
        Dispatches a notification to the user's channels.
        """
        templates = NOTIFICATION_TEMPLATES.get(self.event_key, {})
        forced_channels = FORCED_CHANNELS.get(self.event_key, set())
        channels = forced_channels or get_channels_for_role(self.event_key, self.role)

        if not templates:
            logger.warning(f"No templates found for event key: {self.event_key}. Using default.")
            templates = {'email': 'default_template.html', 'in_app': 'default_template.html'}

        context = self.context.copy()
        context.update({
            'user': self.user,
            'event_key': self.event_key,
            'role': self.role,
            'website': getattr(self.user, 'website', None),
            'templates': templates,
            'forced_channels': forced_channels,
            'event': self.event_key,
            'payload': self.context.get('payload', {}),
            'notification': Notification(
                user=self.user,
                type='notification',
                title=context.get('title', 'Notification'),
                message=context.get('message', 'You have a new notification.'),
                website=context.get('website', None)
            )
        })

        rendered = NotificationTemplateEngine.render_template(templates, context)

        for channel in channels:
            try:
                self._send_via_channel(channel, context, rendered.get(channel, ''))
                logger.info(f"Notification via {channel} sent for {self.event_key} to user {self.user.id}.")
            except Exception as e:
                logger.error(
                    f"[{self.event_key}] Failed via {channel} for user {self.user.id}: {str(e)}",
                    exc_info=True
                )

    @staticmethod
    def emit_event(event_name: str, context: dict):
        """
        Async trigger to dispatch all templates tied to an event.
        """
        templates = get_templates_for_event(event_name)
        for template in templates:
            send_notification_task.delay(
                event_name=event_name,
                channel=template.channel,
                role=template.role,
                context=context,
                template_name=template.template_name,
            )

    def _send_via_channel(self, channel: str, context: dict, message: str):
        """
        Channel-specific sending logic. Plug in new channels easily here.
        """
        user = context.get("user")

        if channel == "email":
            if user and user.email:
                send_mail(
                    subject=context.get("subject", "Notification"),
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            else:
                raise ValueError("Email channel selected, but user has no email.")

        elif channel == "in_app":
            Notification.objects.create(
                user=user,
                type='in_app',
                title=context.get("title", "Notification"),
                message=message,
                website=context.get("website")
            )

        elif channel == "webhook":
            url = context.get("webhook_url")
            if not url:
                raise ValueError("Webhook URL missing in context.")
            requests.post(url, json={"message": message})

        elif channel == "websocket":
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer # type: ignore
            group = f"notifications_{user.id}"
            channel_layer = get_channel_layer()
            if not channel_layer:
                raise RuntimeError("No channel layer configured.")
            async_to_sync(channel_layer.group_send)(group, {
                "type": "send_notification",
                "message": message
            })

        elif channel == "sms":
            phone = getattr(user.profile, "phone_number", None)
            if not phone:
                raise ValueError("No phone number available for SMS.")
            logger.info(f"SMS sent to {phone}: {message}")
            # Replace with actual SMS service

        elif channel == "telegram":
            from notifications_system.delivery.telegram import TelegramBackend
            telegram_backend = TelegramBackend(notification=self.notification)
            telegram_backend.send()

        # TO DO: Add more channels as needed

        else:
            raise ValueError(f"Unknown channel: {channel}")
        
    @staticmethod
    def create_user_status_records(notification, users):
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus
        )

        NotificationsUserStatus.objects.bulk_create([
            NotificationsUserStatus(
                user=user,
                notification=notification
            )
            for user in users
        ])

    @staticmethod
    def notify_errors(notification, users):
        """
        Notify users about errors in notification delivery.
        """
        for user in users:
            Notification.objects.create(
                user=user,
                type='error',
                title='Notification Delivery Error',
                message=f"Failed to deliver notification: {notification.title}",
                website=notification.website
            )
            logger.error(f"Error notification sent to user {user.id} for notification {notification.id}.")