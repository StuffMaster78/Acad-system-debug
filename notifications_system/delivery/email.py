from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from django.template.loader import render_to_string

from notifications_system.delivery.base import (
    BaseDeliveryBackend,
    DeliveryResult,
)
from notifications_system.registry.template_registry import (
    get_template,
    get_template_name,
)
from notifications_system.utils.email_helpers import send_website_mail

logger = logging.getLogger(__name__)


class EmailBackend(BaseDeliveryBackend):
    """Email delivery backend with hybrid rendering.

    Flow:
      1) Render the class-based template for subject/text/html fallback.
      2) If a file skin is registered or explicitly provided, render it
         and use as HTML body; otherwise use class HTML.
      3) Send via tenant-aware mail utility.

    Channel config keys:
      * template: Optional template path to override the registry skin.
      * email_override: Optional recipient email override.

    Returns:
      DeliveryResult indicating success, message, and provider meta.
    """

    channel = "email"

    def send(self) -> DeliveryResult:
        event = self.notification.event
        payload: Dict[str, Any] = dict(self.notification.payload or {})
        cfg: Dict[str, Any] = dict(self.channel_config or {})
        user = self.user
        website = self.website

        tmpl = get_template(event)
        if not tmpl:
            return DeliveryResult(
                success=False,
                message=f"No class template for '{event}'",
            )

        try:
            title, text_msg, html_msg = tmpl.render(payload)
        except Exception as exc:  # noqa: BLE001
            logger.exception("EmailBackend render failed for '%s': %s", event, exc)
            return DeliveryResult(False, f"render failed: {exc}")

        ctx = {
            **payload,
            "_rendered": {"title": title, "text": text_msg, "html": html_msg},
            "_user": user,
            "_website": website,
            "_notification": self.notification,
            "_config": cfg,
        }

        skin: Optional[str] = None
        try:
            reg_skin = get_template_name(event, "email")
            if reg_skin and reg_skin != "default_template.html":
                skin = reg_skin
        except Exception:  # noqa: BLE001
            # Registry may not provide an email skin; not fatal.
            skin = None

        # Allow explicit override in channel config.
        skin = cfg.get("template") or skin

        html_body: Optional[str] = None
        if skin:
            try:
                html_body = render_to_string(skin, ctx)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "EmailBackend skin render failed for '%s': %s", event, exc
                )
                html_body = None

        html_body = html_body or html_msg
        subject = payload.get("title") or self.notification.title or title
        text_body = payload.get("message") or self.notification.message or text_msg

        to_email = cfg.get("email_override") or getattr(user, "email", None)
        if not to_email:
            return DeliveryResult(
                success=False,
                message="No recipient email (missing user.email and override)",
            )

        try:
            send_website_mail(
                subject=subject,
                message=text_body or "",
                html_message=html_body,
                recipient_list=[to_email],
                website=website,
            )
            return DeliveryResult(
                success=True,
                message="email sent",
                meta={"to": to_email, "skin": skin or "class_html"},
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "EmailBackend send failed for '%s' to %s: %s",
                event,
                to_email,
                exc,
            )
            return DeliveryResult(
                success=False,
                message=f"send failed: {exc}",
                meta={"to": to_email, "skin": skin or "class_html"},
            )

    def supports_retry(self) -> bool:
        """Return True because email is typically safe to retry."""
        return True
