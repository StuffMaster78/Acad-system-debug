"""
Email provider abstraction with registry pattern.
Easily extendable for future providers.
"""

from django.core.mail import EmailMultiAlternatives
import logging

PROVIDER_REGISTRY = {}


def register_provider(name):
    """
    Decorator to register a provider class.
    """
    def decorator(cls):
        PROVIDER_REGISTRY[name.lower()] = cls
        return cls
    return decorator


class EmailProviderBase:
    """
    Abstract base class for all email providers.
    """
    def send_email(self, subject, body_html, from_email, to):
        raise NotImplementedError


@register_provider("smtp")
class SMTPProvider(EmailProviderBase):
    def send_email(self, subject, body_html, from_email, to):
        msg = EmailMultiAlternatives(subject, "", from_email, to)
        msg.attach_alternative(body_html, "text/html")
        msg.send()


# Optional: Add your SendGrid and Mailgun implementations
# You’ll need to install these packages:
#   pip install sendgrid mailgun-python

# Example: SendGrid
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

# @register_provider("sendgrid")
# class SendGridProvider(EmailProviderBase):
#     def __init__(self, api_key):
#         self.client = SendGridAPIClient(api_key=api_key)

#     def send_email(self, subject, body_html, from_email, to):
#         message = Mail(
#             from_email=from_email,
#             to_emails=to,
#             subject=subject,
#             html_content=body_html
#         )
#         self.client.send(message)


# Example: Mailgun
# import requests

# @register_provider("mailgun")
# class MailgunProvider(EmailProviderBase):
#     def __init__(self, api_key, domain):
#         self.api_key = api_key
#         self.domain = domain

#     def send_email(self, subject, body_html, from_email, to):
#         return requests.post(
#             f"https://api.mailgun.net/v3/{self.domain}/messages",
#             auth=("api", self.api_key),
#             data={
#                 "from": from_email,
#                 "to": to,
#                 "subject": subject,
#                 "html": body_html
#             }
#         )


def get_provider_client(campaign):
    """
    Returns the appropriate provider client for the campaign.
    Falls back to SMTP if no integration is active.
    """
    integration = getattr(campaign.website, 'email_service', None)
    if not integration or not integration.is_active:
        return SMTPProvider()

    provider_name = integration.provider_name.lower()
    provider_class = PROVIDER_REGISTRY.get(provider_name)

    if not provider_class:
        raise ValueError(f"Unsupported provider: {provider_name}")

    try:
        return provider_class(api_key=integration.api_key)
    except TypeError:
        return provider_class()  # For SMTP (no api_key needed)
    except Exception as e:
        logging.error(f"Failed to init provider {provider_name}: {e}")
        raise