import json
import logging
from typing import Any, Dict, Optional

import requests  # type: ignore
from django.conf import settings

from .base import BaseDeliveryBackend
from notifications_system.utils.signing import hmac_sign

logger = logging.getLogger(__name__)


class WebhookBackend(BaseDeliveryBackend):
    """POST payload to a remote webhook with optional HMAC signing.

    channel_config:
        url (str): Destination endpoint (required).
        timeout (int): Per-request timeout seconds.
        secret (str): Override for HMAC secret.
        algo (str): 'sha1' or 'sha256'.
        headers (dict): Extra headers to include.
        include_rendered (bool): Include rendered fields in payload.
    """

    def send(self) -> bool:
        cfg = self.channel_config or {}
        url = cfg.get("url")
        if not url:
            logger.warning("Webhook url missing.")
            return False

        # Build payload
        n = self.notification
        base: Dict[str, Any] = {
            "event": n.event,
            "user_id": getattr(n.user, "id", None),
            "website_id": getattr(n.website, "id", None),
            "priority": n.priority,
            "is_critical": n.is_critical,
            "created_at": getattr(n, "created_at", None).isoformat()
            if getattr(n, "created_at", None) else None,
            "payload": n.payload or {},
        }

        if cfg.get("include_rendered", True):
            base.update({
                "title": n.rendered_title or n.title,
                "message": n.rendered_message or n.message,
                "link": n.rendered_link,
            })

        body = json.dumps(base, separators=(",", ":"), ensure_ascii=False)
        data = body.encode("utf-8")

        timeout = cfg.get("timeout") or getattr(
            settings, "WEBHOOK_DEFAULT_TIMEOUT", 5
        )
        algo = cfg.get("algo") or getattr(
            settings, "WEBHOOK_HMAC_ALGO", "sha256"
        )
        secret = cfg.get("secret") or getattr(
            settings, "WEBHOOK_SECRET", ""
        )

        headers = {
            "Content-Type": "application/json",
        }
        headers.update(cfg.get("headers") or {})

        # Optional HMAC signature
        if secret:
            sig = hmac_sign(data, secret, algo=algo)
            sig_header = getattr(
                settings, "WEBHOOK_HMAC_HEADER", "X-Notif-Signature"
            )
            headers[sig_header] = f"{algo}={sig}"

        try:
            resp = requests.post(url, data=data, headers=headers,
                                 timeout=timeout)
            ok = 200 <= resp.status_code < 300
            if not ok:
                logger.warning(
                    "Webhook non-2xx (%s): %s",
                    resp.status_code, resp.text[:500],
                )
            return ok
        except Exception as exc:  # noqa: BLE001
            logger.exception("Webhook send failed: %s", exc)
            return False

    def supports_retry(self) -> bool:
        return True