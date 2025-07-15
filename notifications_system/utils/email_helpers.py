from django.core.mail import send_mail
from django.conf import settings
import logging

from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from notifications_system.models import Notification, NotificationPreference
import logging


logger = logging.getLogger(__name__)



def get_website_sender_email(website=None):
    """
    Get sender email from website config, domain, or settings.
    Raises if no valid fallback exists.
    """
    if website and getattr(website, 'no_reply_email', None):
        return website.no_reply_email

    if website and getattr(website, 'domain', None):
        domain = website.domain.replace("https://", "").replace("http://", "").strip("/")
        return f"no-reply@{domain}"

    default_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if default_email:
        return default_email

    raise ValueError(
        "Missing sender email. Set no_reply_email on the Website model or DEFAULT_FROM_EMAIL in settings."
    )


def send_website_mail(subject, message, recipient_list, website=None, html_message=None):
    """
    Sends tenant-aware email using sender from Website config.
    """
    from_email = get_website_sender_email(website)

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Email sent from {from_email} to {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}", exc_info=True)
        return False