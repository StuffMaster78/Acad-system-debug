"""
A module to send notifications to users
across multiple channels like email, in-app, SMS, and push.
It handles user preferences, notification creation,
and sending logic, ensuring notifications are sent
according to user settings and system requirements.
"""
import logging
from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from notifications_system.models.notifications import Notification
from notifications_system.models.notification_preferences import (
    NotificationPreference
)
from notifications_system.utils.email_helpers import send_website_mail
from notifications_system.enums import NotificationPriority
from websites.models import Website

logger = logging.getLogger(__name__)

def send_notification(
    user,
    title,
    message,
    *,
    link=None,
    website=None,
    type="in_app",
    category="info",
    context=None,
    meta=None,
    force=False
):
    """
    Send a structured, multi-channel notification to a user based on their preferences.

    Args:
        user (User): Recipient.
        title (str): Notification title.
        message (str): Notification content.
        link (str): Relative link (e.g., 'orders/123').
        website (Website): Optional website instance.
        type (str): 'in_app', 'email', 'sms', 'push', etc.
        category (str): 'info', 'warning', 'error', 'announcement'.
        context (dict): Additional context for templates.
        meta (dict): Extra metadata for frontend use.
        force (bool): Override user preferences if True.

    Returns:
        Notification: The created notification object (even if not actually sent).
    """
    if not website:
        website = getattr(user, 'website', None)
    if not website:
        raise ImproperlyConfigured(
            "Website must be provided or resolvable from the user."
        )

    context = context or {}
    meta = meta or {}

    preferences = getattr(user, 'notification_preferences', None)
    if preferences is None:
        preferences = NotificationPreference.objects.filter(
            user=user, website=website
        ).first()

    # Respect user preferences unless forced
    if not force and preferences:
        if type == "email" and not preferences.receive_email:
            logger.info(f"Skipping email: {user} opted out.")
            return None
        if type == "in_app" and not preferences.receive_in_app:
            logger.info(f"Skipping in-app: {user} opted out.")
            return None
        if type == "sms" and not preferences.receive_sms:
            logger.info(f"Skipping SMS: {user} opted out.")
            return None
        if type == "push" and not preferences.receive_push:
            logger.info(f"Skipping push: {user} opted out.")
            return None

    # Handle full URL for frontend link
    full_link = None
    if link:
        full_link = f"{website.domain.rstrip('/')}/{link.lstrip('/')}"
        context["link"] = full_link
        meta["link"] = link

    # Create and optionally send
    notification = Notification.objects.create(
        website=website,
        user=user,
        type=type,
        title=title,
        message=message,
        status="pending",
        sent_at=now(),
        category=category,
        delivery_attempts=1,
    )

    try:
        if type == "email":
            send_website_mail(
                subject=title,
                message=message,
                recipient_list=[user.email],
                website=website,
                html_message=context.get("html_message")
            )
        elif type == "in_app":
            # Already persisted, nothing else needed
            pass
        elif type == "sms":
            # TODO: integrate SMS sending here
            logger.info(f"Stub: SMS to {user.username} - {message}")
        elif type == "push":
            # TODO: integrate push notification service
            logger.info(f"Stub: Push to {user.username} - {message}")
        else:
            logger.warning(f"Unknown notification type: {type}")
            notification.status = "failed"
            notification.save()
            return notification

        notification.status = "sent"
        notification.save()
        return notification

    except Exception as e:
        logger.error(f"Failed to send {type} notification to {user}: {e}", exc_info=True)
        notification.status = "failed"
        notification.save()
        return notification
    
def send_sms_notification(user, message):
    """
    Send an SMS notification to a user.
    This is a stub function for future SMS integration.
    """
    logger.info(f"Stub: SMS to {user.username} - {message}")
    # Here you would integrate with an SMS service like Twilio, Nexmo, etc.
    return True

def send_push_notification(user, message):
    """
    Send a push notification to a user.
    This is a stub function for future push notification integration.
    """
    logger.info(f"Stub: Push to {user.username} - {message}")
    # Here you would integrate with a push notification service like Firebase, OneSignal, etc.
    return True

def send_in_app_notification(user, title, message, context=None):
    """
    Send an in-app notification to a user.
    This is a stub function for future in-app notification integration.
    """
    context = context or {}
    context["title"] = title
    context["message"] = message
    # Here you would integrate with your in-app notification system
    logger.info(f"In-app notification to {user.username}: {title} - {message}")
    return True

def send_ws_notification(user, message):
    """
    Send a WebSocket notification to a user.
    This is a stub function for future WebSocket integration.
    """
    logger.info(f"Stub: WebSocket to {user.username} - {message}")
    # Here you would integrate with your WebSocket server
    return True