from django.core.mail import send_mail
from django.conf import settings
import logging

from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from notifications_system.models.notifications import Notification
from notifications_system.models.notification_preferences import NotificationPreference
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from notifications_system.enums import NotificationPriority
from notifications_system.utils.template_priority import get_template_for_priority
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


def send_website_mail(
        subject, message, recipient_list,
        website=None, html_message=None
):
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
    
def send_priority_email(
    user, subject, message, context=None,
    priority=NotificationPriority.NORMAL, website=None
):
    """
    Sends an email with priority handling.
    Uses the appropriate template based on priority.
    """
    context = context or {}
    context.update({
        "user": user,
        "subject": subject,
        "message": message,
            "website_name": getattr(website, "name", "Our Platform"),
        })

    html_content = render_to_string(get_template_for_priority(priority), context)

    email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=website.get_from_email() if website else "no-reply@example.com",
            to=[user.email]
        )
    email.attach_alternative(html_content, "text/html")
    email.send()