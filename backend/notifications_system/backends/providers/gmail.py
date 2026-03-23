# notifications_system/backends/providers/gmail.py
"""
Gmail SMTP backend for development and testing.
Uses Django's built-in SMTP email backend under the hood.

Setup:
    1. Enable 2-Factor Authentication on your Google account
    2. Go to Google Account → Security → App Passwords
    3. Generate an App Password for 'Mail'
    4. Use that password — NOT your regular Gmail password

Never use this in production. Use SendGrid/Mailgun/SES instead.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from notifications_system.backends.providers.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class GmailBackend(BaseEmailBackend):
    """
    Sends email via Gmail SMTP.
    For development and testing only.

    Required config:
        email:    your Gmail address
        password: your Gmail App Password (not your login password)

    Optional config:
        port:     SMTP port (default 587)
    """

    def send(
        self,
        *,
        to: str,
        subject: str,
        body_html: str,
        body_text: str,
        from_name: str,
        from_address: str,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        from django.core.mail import EmailMultiAlternatives
        from django.core.mail.backends.smtp import EmailBackend as DjangoSMTP

        gmail_email = self.config.get('email')
        gmail_password = self.config.get('password')

        if not gmail_email or not gmail_password:
            raise RuntimeError(
                "Gmail backend requires 'email' and 'password' in config."
            )

        # Build the email
        from_header = (
            f"{from_name} <{from_address}>"
            if from_name and from_address
            else gmail_email
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_header,
            to=[to],
            reply_to=[reply_to] if reply_to else [],
        )
        if body_html:
            msg.attach_alternative(body_html, 'text/html')

        # Send via Gmail SMTP
        backend = DjangoSMTP(
            host='smtp.gmail.com',
            port=self.config.get('port', 587),
            username=gmail_email,
            password=gmail_password,
            use_tls=True,
            fail_silently=False,
        )

        try:
            backend.open()
            msg.connection = backend
            msg.send()
            backend.close()

            logger.info(
                "GmailBackend: sent to=%s subject=%s.", to, subject
            )
            return {'message_id': f"gmail:{to}:{subject[:20]}"}

        except Exception as exc:
            logger.exception(
                "GmailBackend: failed to=%s: %s.", to, exc
            )
            raise