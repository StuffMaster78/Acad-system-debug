from django.core.mail import send_mail
from websites.models import Website, WebsiteSettings
from django.conf import settings
from django.urls import reverse
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



def send_password_reset_email(user, token, request=None):
    """
    Sends a password reset email to the user with a reset link.

    Args:
        user (User): The user to send the email to.
        token (str): The reset token to include in the link.
        request (HttpRequest, optional): Used to build full URL.
    """
    site = request.get_host() if request else "example.com"
    scheme = "https" if request and request.is_secure() else "http"
    reset_path = reverse("auth:password-reset-confirm")
    reset_url = f"{scheme}://{site}{reset_path}?token={token}"

    subject = "Reset your password"
    message = (
        f"Hi {user.get_full_name() or user.username},\n\n"
        "You requested a password reset. Click the link below to reset your "
        f"password:\n\n{reset_url}\n\n"
        "If you didn’t request this, just ignore this email."
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )