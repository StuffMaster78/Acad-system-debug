from django.core.mail import send_mail
from websites.models import Website, WebsiteSettings
import logging

logger = logging.getLogger(__name__)

def send_custom_email(user, subject, body, website_id):
    sender_name, sender_email, _ = get_email_sender_details(website_id)
    try:
        send_mail(
            subject,
            body.strip(),
            f"{sender_name} <{sender_email}>",
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {str(e)}")
        raise Exception(f"Failed to send email to {user.email}: {str(e)}")

def get_email_sender_details(website_id, type="notification"):
    """
    Returns the sender name, email address,
    and domain based on the email type.
    Fetches these details from the WebsiteSettings
    model specific to the website.
    """
    try:
        website = Website.objects.get(id=website_id)
        website_settings = website.settings.first()
        if website_settings:
            sender_name = website_settings.sender_name
            sender_email = website_settings.sender_email
            domain = website.domain_url
        else:
            raise WebsiteSettings.DoesNotExist
    except Website.DoesNotExist:
        raise ValueError(f"Website with ID {website_id} does not exist.")
    except WebsiteSettings.DoesNotExist:
        raise ValueError(f"No settings found for Website with ID {website_id}.")
    
    return sender_name, sender_email, domain