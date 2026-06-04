"""
Email provider abstraction with registry pattern.

Supported providers:
  smtp      - Django built-in mail backend (default)
  sendgrid  - SendGrid v3 Mail Send API (no extra SDK required)
  mailgun   - Mailgun Messages API (no extra SDK required)

Mailgun note: store the api_key field as "{mailgun_api_key}:{sending_domain}",
e.g. key-abc123:mg.yourdomain.com  (colon separator required).
"""

import logging
import re

import requests as http_requests
from django.core.mail import EmailMultiAlternatives

log = logging.getLogger(__name__)

PROVIDER_REGISTRY = {}


def register_provider(name):
    def decorator(cls):
        PROVIDER_REGISTRY[name.lower()] = cls
        return cls
    return decorator


class EmailProviderBase:
    def send_email(self, subject, body_html, from_email, to):
        raise NotImplementedError


@register_provider("smtp")
class SMTPProvider(EmailProviderBase):
    def send_email(self, subject, body_html, from_email, to):
        msg = EmailMultiAlternatives(subject, "", from_email, to)
        msg.attach_alternative(body_html, "text/html")
        msg.send()


@register_provider("sendgrid")
class SendGridProvider(EmailProviderBase):
    """
    Sends via the SendGrid v3 Mail Send API.
    No sendgrid SDK required - only the requests package.
    """

    _API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self, api_key):
        self._api_key = api_key

    def send_email(self, subject, body_html, from_email, to):
        from_name, from_addr = _parse_address(from_email)
        from_field = {"email": from_addr}
        if from_name:
            from_field["name"] = from_name

        payload = {
            "personalizations": [
                {"to": [{"email": addr} for addr in to]}
            ],
            "from": from_field,
            "subject": subject,
            "content": [{"type": "text/html", "value": body_html}],
        }
        resp = http_requests.post(
            self._API_URL,
            json=payload,
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        if resp.status_code not in (200, 202):
            log.error("SendGrid API error %s: %s", resp.status_code, resp.text)
            resp.raise_for_status()


@register_provider("mailgun")
class MailgunProvider(EmailProviderBase):
    """
    Sends via the Mailgun Messages API.
    No mailgun SDK required - only the requests package.

    Store api_key as:  {mailgun_api_key}:{sending_domain}
    Example:           key-abc1234567890:mg.yourplatform.com
    """

    _API_BASE = "https://api.mailgun.net/v3"

    def __init__(self, api_key):
        if ":" not in api_key:
            raise ValueError(
                "Mailgun api_key must be stored as {key}:{domain}. "
                "Example: key-abc123:mg.yourdomain.com"
            )
        self._key, self._domain = api_key.split(":", 1)

    def send_email(self, subject, body_html, from_email, to):
        resp = http_requests.post(
            self._API_BASE + "/" + self._domain + "/messages",
            auth=("api", self._key),
            data={
                "from": from_email,
                "to": to,
                "subject": subject,
                "html": body_html,
            },
            timeout=30,
        )
        if not resp.ok:
            log.error("Mailgun API error %s: %s", resp.status_code, resp.text)
            resp.raise_for_status()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ADDR_RE = re.compile(r"^(.*?)\s*<([^>]+)>$")


def _parse_address(address):
    """Parse 'Display Name <email>' or plain 'email'. Returns (name, email)."""
    clean = address.strip()
    m = _ADDR_RE.match(clean)
    if m:
        name = m.group(1).strip().strip('"')
        return name, m.group(2).strip()
    return "", clean


def get_provider_client(campaign):
    """
    Returns the appropriate provider client for the campaign.
    Falls back to SMTP if no active integration is configured.
    """
    integration = getattr(campaign.website, "email_service", None)
    if not integration or not integration.is_active:
        return SMTPProvider()

    provider_name = integration.provider_name.lower()
    provider_class = PROVIDER_REGISTRY.get(provider_name)

    if not provider_class:
        raise ValueError("Unsupported email provider: " + provider_name)

    try:
        return provider_class(api_key=integration.api_key)
    except TypeError:
        return provider_class()
    except Exception as exc:
        log.error("Failed to init provider %s: %s", provider_name, exc)
        raise
