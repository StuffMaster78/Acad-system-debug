import logging
from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from notifications_system.models import Notification, NotificationPreference
from notifications_system.utils.email_helpers import send_website_mail
from notifications_system.notification_enums import NotificationPriority
from notifications_system.models import Website

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
        raise ImproperlyConfigured("Website must be provided or resolvable from the user.")

    context = context or {}
    meta = meta or {}

    preferences = getattr(user, 'notification_preferences', None)
    if preferences is None:
        preferences = NotificationPreference.objects.filter(user=user, website=website).first()

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