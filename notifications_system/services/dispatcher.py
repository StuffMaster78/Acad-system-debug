import logging
from core.utils.email_helpers import send_website_mail
from core.utils.notifications import send_notification  # In-app helper

logger = logging.getLogger(__name__)

def notify_user(user, subject, message, *, tenant=None, html_message=None,
                channels=None):
    """
    Centralized notification dispatcher: handles in-app + email + future push 
    support.
    
    Args:
        user: The user to notify.
        subject: Title/subject of the notification.
        message: Body text.
        tenant: Tenant or site object for email customization.
        html_message: Optional HTML content for email.
        channels: Optional list like ['email', 'in_app'] to control where 
                  to send.
    """
    subject = subject or "Notification"
    message = message or "You have a new notification"
    channels = channels or ['email', 'in_app']

    logger.info(f"Dispatching notification to {user} via channels: {channels}")

    if 'in_app' in channels:
        try:
            send_notification(
                user=user,
                title=subject,
                message=message
            )
            logger.debug(f"In-app notification sent to {user}")
        except Exception as e:
            logger.error(f"In-app notification failed for {user}: {e}", 
                         exc_info=True)

    if 'email' in channels and getattr(user, 'email', None):
        try:
            send_website_mail(
                subject=subject,
                message=message,
                recipient_list=[user.email],
                tenant=tenant,
                html_message=html_message
            )
            logger.debug(f"Email sent to {user.email}")
        except Exception as e:
            logger.error(f"Email notification failed for {user.email}: {e}",
                         exc_info=True)

def notify_users(users, subject, message, *, tenant=None, html_message=None,
                 channels=None):
    """
    Bulk version of notify_user to send notifications to a list of users.
    """
    for user in users:
        notify_user(user, subject, message, tenant=tenant, 
                    html_message=html_message, channels=channels)