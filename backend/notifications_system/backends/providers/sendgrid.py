# notifications_system/backends/providers/sendgrid.py
"""SendGrid email provider backend."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from backend.notifications_system.backends.providers.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class SendGridBackend(BaseEmailBackend):
    """
    Sends email via SendGrid API.
    Requires config: {'api_key': 'SG.xxx'}
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
        try:
            import sendgrid
            from sendgrid.helpers.mail import (
                Mail, To, From, Subject,
                PlainTextContent, HtmlContent, ReplyTo,
            )
        except ImportError:
            raise RuntimeError(
                "sendgrid package is not installed. "
                "Run: pip install sendgrid"
            )

        api_key = self.config.get('api_key')
        if not api_key:
            raise RuntimeError("SendGrid api_key is not configured.")

        message = Mail(
            from_email=From(from_address, from_name),
            to_emails=To(to),
            subject=Subject(subject),
            plain_text_content=PlainTextContent(body_text),
            html_content=HtmlContent(body_html),
        )
        if reply_to:
            message.reply_to = ReplyTo(reply_to)

        client = sendgrid.SendGridAPIClient(api_key=api_key)
        response = client.send(message)

        message_id = dict(response.headers).get('X-Message-Id', '')
        logger.info(
            "SendGridBackend: sent to=%s status=%s message_id=%s.",
            to, response.status_code, message_id,
        )
        return {'message_id': message_id, 'status_code': response.status_code}