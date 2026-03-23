# notifications_system/backends/email.py
"""
Email delivery backend.
Receives a pre-rendered Delivery instance and sends via the
website's configured email provider backend.
"""
from __future__ import annotations

import logging

from notifications_system.backends.base import BaseDeliveryBackend, DeliveryResult

logger = logging.getLogger(__name__)


class EmailBackend(BaseDeliveryBackend):
    """
    Sends email notifications via the website's configured email provider.

    Expects delivery.rendered to contain:
        subject:    Email subject line
        body_html:  HTML email body
        body_text:  Plain text fallback

    All rendering is done by TemplateService before this backend is called.
    This backend is responsible only for the actual send.
    """

    channel = 'email'

    def send(self) -> DeliveryResult:
        user = self.user
        website = self.website
        rendered = self.rendered

        # --- Validate recipient
        to_email = getattr(user, 'email', None)
        if not to_email:
            return DeliveryResult(
                success=False,
                message='No recipient email — user.email is empty.',
                error_code='NO_EMAIL',
            )

        # --- Validate rendered content
        subject = rendered.get('subject', '').strip()
        body_html = rendered.get('body_html', '').strip()
        body_text = rendered.get('body_text', '').strip()

        if not subject:
            logger.warning(
                "EmailBackend: empty subject for delivery=%s event=%s.",
                self.delivery.id,
                self.delivery.event_key,
            )

        if not body_html and not body_text:
            return DeliveryResult(
                success=False,
                message='No rendered body — both body_html and body_text are empty.',
                error_code='NO_BODY',
            )

        # --- Resolve provider backend for this website
        try:
            from notifications_system.services.email_service import EmailService
            provider = EmailService.get_backend(website)
        except Exception as exc:
            logger.error(
                "EmailBackend: could not resolve provider for website=%s: %s.",
                getattr(website, 'id', None),
                exc,
            )
            return DeliveryResult(
                success=False,
                message=f"Provider resolution failed: {exc}",
                error_code='NO_PROVIDER',
            )

        # --- Resolve sender identity
        try:
            from notifications_system.models.notification_settings import (
                GlobalNotificationSystemSettings,
            )
            ws_settings = GlobalNotificationSystemSettings.for_website(website)
            from_name = ws_settings.email_from_name or 'Notifications'
            from_address = ws_settings.email_from_address or ''
            reply_to = ws_settings.email_reply_to or None
        except Exception:
            from_name = 'Notifications'
            from_address = ''
            reply_to = None

        # --- Send
        try:
            result = provider.send(
                to=to_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                from_name=from_name,
                from_address=from_address,
                reply_to=reply_to,
            )
            return DeliveryResult(
                success=True,
                message='Email sent.',
                provider_msg_id=result.get('message_id', ''),
                meta={'to': to_email},
            )
        except Exception as exc:
            logger.exception(
                "EmailBackend: send failed for delivery=%s to=%s: %s.",
                self.delivery.id,
                to_email,
                exc,
            )
            return DeliveryResult(
                success=False,
                message=f"Send failed: {exc}",
                error_code='SEND_ERROR',
                meta={'to': to_email},
            )