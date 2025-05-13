# notifications_system/services/notification_service.py
from notifications_system.models import Notification
from core.utils.email_helpers import send_website_mail
from core.utils.sms_helpers import send_sms_notification
from core.utils.push_helpers import send_push_notification
from core.utils.ws_helpers import send_ws_notification
from django.utils.timezone import now
from django.conf import settings

def send_notification(recipient, title, message, category="in_app"):
    """
    Send a notification to a user.

    :param recipient: User receiving the notification
    :param title: Notification title
    :param message: Notification content
    :param category: Type of notification (in_app, email, SMS, push)
    """
    # Create Notification object and set initial status
    notification = Notification.objects.create(
        user=recipient,
        type=category,
        title=title,
        message=message,
        status="pending",
        category=category,
        sent_at=None,
    )

    # Check user preferences before sending
    preferences = recipient.notification_preferences
    if not preferences:
        return notification  # If no preferences, don't proceed

    if category == 'email' and not preferences.receive_email:
        return notification  # Skip if the user has disabled email notifications

    if category == 'sms' and not preferences.receive_sms:
        return notification  # Skip if the user has disabled SMS notifications

    if category == 'push' and not preferences.receive_push:
        return notification  # Skip if the user has disabled push notifications

    if category == 'in_app' and not preferences.receive_in_app:
        return notification  # Skip if the user has disabled in-app notifications

    # Simulate sending (extend to use actual services)
    if category == 'email':
        send_website_mail(recipient.email, title, message)
    elif category == 'sms':
        send_sms_notification(recipient, message)
    elif category == 'push':
        send_push_notification(recipient, message)
    elif category == 'in_app':
        send_ws_notification(recipient, message)
    
    # Mark the notification as sent
    notification.status = 'sent'
    notification.sent_at = now()
    notification.save()

    return notification


def notify_admin_of_error(error_message: str) -> None:
    """
    Notify admin about an error via the notification system.
    """
    send_notification(
        subject='Discount Application Error',
        message=error_message,
        recipients=[settings.ADMIN_EMAIL],
        notification_type='error',  # or whatever your system expects
    )