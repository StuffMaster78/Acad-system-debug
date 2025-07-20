from notifications_system.template_engine import NotificationTemplateEngine
from notifications_system.registry.role_bindings import get_channels_for_role
from notifications_system.registry.template_registry import NOTIFICATION_TEMPLATES
from notifications_system.registry.forced_channels import FORCED_CHANNELS
from notifications_system.template_engine import NotificationTemplateEngine
from notifications_system.registry.template_registry import get_templates_for_event
from notifications_system.tasks import send_notification_task
import logging

logger = logging.getLogger(__name__)

class NotificationDispatcher:
    """
    A class responsible for dispatching notifications based on event keys and user roles.
    """
    def __init__(self, user, event_key: str, context: dict, role: str = None):
        self.user = user
        self.event_key = event_key
        self.context = context
        self.role = role or getattr(user, 'role', 'client')  # Default to 'client' if no role is set


    def emit_event(event_name, context):
        """
        Emits an event by dispatching notifications to
        all registered templates for that event.
        """
        templates = get_templates_for_event(event_name)
        for template in templates:
           send_notification_task .delay(
                event_name=event_name,
                channel=template.channel,
                role=template.role,
                context=context,
                template_name=template.template_name
            )

    @staticmethod
    def dispatch_notification(self):
        """
        Dispatches a notification based on the event key and context.
        """
        templates = NOTIFICATION_TEMPLATES.get(self.event_key, {})
        forced_channels = FORCED_CHANNELS.get(self.event_key, set())
        channels = forced_channels or get_channels_for_role(self.event_key, self.role)
        if not templates:
            logger.warning(f"No templates found for event key: {self.event_key}. Using default template.")
            templates = {'email': 'default_template.html', 'in_app': 'default_template.html'}
        context = self.context.copy()
        context['user'] = self.user
        context['event_key'] = self.event_key
        context['role'] = self.role 


        rendered = NotificationTemplateEngine.render_template(templates, context)
        for channel in channels:
            try:
                self.send_message_via_channel(channel, context, rendered.get(channel, ''))
                logger.info(f"Notification sent via {channel} for event {self.event_key} to user {self.user.id}.")
            except Exception as e:
                logger.error(f"Failed to send notification via {channel} for event {self.event_key} to user {self.user.id}: {e}")
                

    @staticmethod
    def send_message_via_channel(
        channel: str, context: dict, message: str
    ):
        if channel == 'email':
            from django.core.mail import send_mail
            from django.conf import settings
            user_email = context.get('user_email')
            if user_email:
                send_mail(
                    subject=context.get('subject', 'Notification'),
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[context['user_email']],
                    fail_silently=False,
                )
        elif channel == 'in_app':
            # Logic for in-app notifications
            from notifications_system.models import Notification
            user = context.get('user')
            if user:
                Notification.objects.create(
                    user=user,
                    type='in_app',
                    title=context.get('title', 'Notification'),
                    message=message,
                    website=context.get('website')
                )
        elif channel == 'webhook':
            # Logic for webhook notifications
            webhook_url = context.get('webhook_url')
            if webhook_url:
                import requests # type: ignore
                requests.post(webhook_url, json={'message': message})
        else:
            logger.warning(f"Unknown channel: {channel}. Cannot send notification.")
            # You might want to raise an exception or handle it accordingly
            raise ValueError(f"Unknown channel: {channel}") 