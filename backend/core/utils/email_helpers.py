from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_website_sender_email(website=None):
    """
    Returns the tenant-specific no-reply email,
    falling back to settings or a generic address.
    """
    if website:
        if getattr(website, 'no_reply_email', None):
            return website.no_reply_email
        if getattr(website, 'domain', None):
            domain = website.domain.replace('https://', '').replace('http://', '').strip('/')
            return f"no-reply@{domain}"
    # Final fallback
    default_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if default_email:
        return default_email
    
    # Production
    # if not default_email:
    #     logger.warning("DEFAULT_FROM_EMAIL is not set. Email may fail or be flagged.")
    #     default_email = "dev-null@localhost.localdomain"  # not fake, but clearly not production
    
    raise ValueError(
        "No sender email could be determined. Set no_reply_email on the Website in settings."
        )

def send_website_mail(
        subject, message,
        recipient_list, website=None,
        html_message=None
):
    """
    Sends email using the tenant's configured no-reply address.
    """
    from_email = get_website_sender_email(website)
    reply_to = [getattr(website, 'support_email', from_email)] if website else [from_email]

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message,
            reply_to=reply_to,
        )
        logger.info(f"Email sent from {from_email} to {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {e}", exc_info=True)
        return False