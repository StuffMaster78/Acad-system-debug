# notifications_system/services/email_service.py
"""
Email delivery service.
Resolves the correct provider backend for a website and sends.
Provider selection order:
    1. Website-specific override in GlobalNotificationSystemSettings
    2. Platform default from Django settings
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Resolves the email provider backend for a website and sends.
    Called by EmailBackend after rendering is complete.
    """

    @staticmethod
    def get_backend(website) -> 'BaseEmailBackend':
        """
        Return the correct email provider backend for a website.
        Website-specific config takes priority over platform default.
        """
        from notifications_system.models.notification_settings import (
            GlobalNotificationSystemSettings,
        )
        from notifications_system.backends.providers.sendgrid import SendGridBackend
        from notifications_system.backends.providers.mailgun import MailgunBackend
        from notifications_system.backends.providers.ses import SESBackend

        provider = None
        config = {}

        # Website-specific override
        try:
            ws_settings = GlobalNotificationSystemSettings.for_website(website)
            if ws_settings.email_provider and ws_settings.email_provider_config:
                provider = ws_settings.email_provider
                config = ws_settings.email_provider_config
        except Exception:
            pass

        # Platform default
        if not provider:
            provider = getattr(settings, 'DEFAULT_EMAIL_PROVIDER', 'console')
            config = getattr(settings, 'DEFAULT_EMAIL_CONFIG', {})

        backend_map = {
            'sendgrid': SendGridBackend,
            'mailgun': MailgunBackend,
            'ses': SESBackend,
            'console': ConsoleEmailBackend,
        }

        backend_cls = backend_map.get(provider)
        if not backend_cls:
            logger.warning(
                "EmailService: unknown provider=%s, falling back to console.",
                provider,
            )
            backend_cls = ConsoleEmailBackend

        return backend_cls(config)

    @staticmethod
    def send_rendered(
        *,
        to_email: str,
        rendered: Dict[str, str],
        website,
        from_name: str = '',
        from_address: str = '',
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a pre-rendered email.
        Called directly by DigestService for digest emails.

        Returns:
            Provider result dict with at minimum {'message_id': str}
        """
        backend = EmailService.get_backend(website)

        try:
            from notifications_system.models.notification_settings import (
                GlobalNotificationSystemSettings,
            )
            ws_settings = GlobalNotificationSystemSettings.for_website(website)
            from_name = from_name or ws_settings.email_from_name or 'Notifications'
            from_address = from_address or ws_settings.email_from_address or ''
            reply_to = reply_to or ws_settings.email_reply_to or None
        except Exception:
            from_name = from_name or 'Notifications'

        return backend.send(
            to=to_email,
            subject=rendered.get('subject', ''),
            body_html=rendered.get('body_html', ''),
            body_text=rendered.get('body_text', ''),
            from_name=from_name,
            from_address=from_address,
            reply_to=reply_to,
        )


class ConsoleEmailBackend:
    """
    Development backend — prints email to console instead of sending.
    Used when DEFAULT_EMAIL_PROVIDER is not configured.
    """

    def __init__(self, config: dict) -> None:
        self.config = config

    def send(
        self,
        *,
        to: str,
        subject: str,
        body_html: str,
        body_text: str,
        from_name: str = '',
        from_address: str = '',
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        logger.info(
            "ConsoleEmailBackend: to=%s subject=%s from=%s",
            to, subject, from_name,
        )
        print(f"\n{'='*60}")
        print(f"TO:      {to}")
        print(f"FROM:    {from_name} <{from_address}>")
        print(f"SUBJECT: {subject}")
        print(f"{'─'*60}")
        print(body_text or body_html)
        print(f"{'='*60}\n")
        return {'message_id': 'console'}