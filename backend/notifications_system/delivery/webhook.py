import json
import logging
from typing import Any, Dict

import requests  # type: ignore
from django.conf import settings

from .base import BaseDeliveryBackend
from notifications_system.utils.signing import hmac_sign

logger = logging.getLogger(__name__)


class WebhookBackend(BaseDeliveryBackend):
    """POST payload to a remote webhook with optional HMAC signing."""

    channel = "webhook"

    def send(self) -> bool:
        cfg = self.channel_config or {}
        url = cfg.get("url")
        if not url:
            logger.warning("Webhook url missing.")
            return False

        notification = self.notification
        base: Dict[str, Any] = {
            "event": notification.event,
            "user_id": getattr(notification.user, "id", None),
            "website_id": getattr(notification.website, "id", None),
            "priority": notification.priority,
            "is_critical": notification.is_critical,
            "created_at": getattr(notification, "created_at", None).isoformat()
            if getattr(notification, "created_at", None)
            else None,
            "payload": notification.payload or {},
        }

        if cfg.get("include_rendered", True):
            base.update(
                {
                    "title": notification.rendered_title or notification.title,
                    "message": notification.rendered_message or notification.message,
                    "link": notification.rendered_link,
                }
            )

        body = json.dumps(base, separators=(",", ":"), ensure_ascii=False)
        data = body.encode("utf-8")

        timeout = cfg.get("timeout") or getattr(
            settings, "WEBHOOK_DEFAULT_TIMEOUT", 5
        )
        algo = cfg.get("algo") or getattr(
            settings, "WEBHOOK_HMAC_ALGO", "sha256"
        )
        secret = cfg.get("secret") or getattr(settings, "WEBHOOK_SECRET", "")

        headers = {"Content-Type": "application/json"}
        headers.update(cfg.get("headers") or {})

        # Optional HMAC signature
        if secret:
            sig = hmac_sign(data, secret, algo=algo)
            sig_header = getattr(
                settings, "WEBHOOK_HMAC_HEADER", "X-Notif-Signature"
            )
            headers[sig_header] = f"{algo}={sig}"

        try:
            resp = requests.post(url, data=data, headers=headers, timeout=timeout)
            ok = 200 <= resp.status_code < 300
            if not ok:
                logger.warning(
                    "Webhook non-2xx (%s): %s",
                    resp.status_code,
                    resp.text[:500],
                )
            return ok
        except Exception as exc:  # noqa: BLE001
            logger.exception("Webhook send failed: %s", exc)
            return False

    def supports_retry(self) -> bool:
        return True

