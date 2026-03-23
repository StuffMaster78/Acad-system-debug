# notifications_system/backends/providers/mailgun.py
"""Mailgun email provider backend."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import requests

from backend.notifications_system.backends.providers.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class MailgunBackend(BaseEmailBackend):
    """
    Sends email via Mailgun API.
    Requires config: {'api_key': 'key-xxx', 'domain': 'mg.yourdomain.com'}
    Optional config: {'eu': True} for EU region.
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
        api_key = self.config.get('api_key')
        domain = self.config.get('domain')

        if not api_key:
            raise RuntimeError("Mailgun api_key is not configured.")
        if not domain:
            raise RuntimeError("Mailgun domain is not configured.")

        base_url = (
            'https://api.eu.mailgun.net/v3'
            if self.config.get('eu')
            else 'https://api.mailgun.net/v3'
        )

        data: Dict[str, Any] = {
            'from': f"{from_name} <{from_address}>",
            'to': to,
            'subject': subject,
            'text': body_text,
            'html': body_html,
        }
        if reply_to:
            data['h:Reply-To'] = reply_to

        response = requests.post(
            f"{base_url}/{domain}/messages",
            auth=('api', api_key),
            data=data,
            timeout=10,
        )
        response.raise_for_status()

        result = response.json()
        message_id = result.get('id', '')
        logger.info(
            "MailgunBackend: sent to=%s message_id=%s.",
            to, message_id,
        )
        return {'message_id': message_id}