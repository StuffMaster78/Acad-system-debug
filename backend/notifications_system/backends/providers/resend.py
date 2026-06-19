"""Resend transactional email provider backend."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import requests

from notifications_system.backends.providers.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class ResendBackend(BaseEmailBackend):
    """Send pre-rendered transactional messages through the Resend API."""

    provider_name = "Resend"
    _API_URL = "https://api.resend.com/emails"

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
        api_key = self.config.get("api_key")
        if not api_key:
            raise RuntimeError("Resend api_key is not configured.")
        if not from_address:
            raise RuntimeError("Resend requires a verified from_address.")

        sender = (
            f"{from_name} <{from_address}>"
            if from_name
            else from_address
        )
        payload: Dict[str, Any] = {
            "from": sender,
            "to": [to],
            "subject": subject,
            "html": body_html,
            "text": body_text,
        }
        if reply_to:
            payload["reply_to"] = reply_to

        response = requests.post(
            self._API_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
        message_id = result.get("id", "")
        logger.info("ResendBackend: sent to=%s message_id=%s.", to, message_id)
        return {"message_id": message_id}
