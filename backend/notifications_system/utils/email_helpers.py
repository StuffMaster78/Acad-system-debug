"""Tenant-aware email helpers for the notifications system."""

from __future__ import annotations

import logging
from typing import Iterable, Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string

from notifications_system.enums import NotificationPriority
from notifications_system.utils.template_priority import (
    get_template_for_priority,
)

logger = logging.getLogger(__name__)


def _domain_from_website(website) -> Optional[str]:
    """Extract bare domain from a website object.

    Args:
        website: Object with a `domain` attribute (URL or bare domain).

    Returns:
        Bare domain (e.g., "example.com") or None.
    """
    if not website or not getattr(website, "domain", None):
        return None
    raw = str(website.domain).strip().rstrip("/")
    # Handle "https://example.com" and "example.com"
    if "://" in raw:
        try:
            from urllib.parse import urlparse  # stdlib import here to stay local
            parsed = urlparse(raw)
            return parsed.hostname or None
        except Exception:  # noqa: BLE001
            return raw.replace("https://", "").replace("http://", "")
    return raw


def get_website_sender_email(website=None) -> str:
    """Resolve a tenant-aware sender email address.

    Resolution order:
      1) `website.no_reply_email` if provided
      2) `no-reply@<website.domain>`
      3) `settings.DEFAULT_FROM_EMAIL`

    Args:
        website: Optional website/tenant object.

    Returns:
        Sender email address.

    Raises:
        ImproperlyConfigured: If no valid sender can be resolved.
    """
    if website and getattr(website, "no_reply_email", None):
        return website.no_reply_email

    domain = _domain_from_website(website)
    if domain:
        return f"no-reply@{domain}"

    default_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if default_email:
        return default_email

    raise ImproperlyConfigured(
        "No sender email configured. Set Website.no_reply_email, or "
        "DEFAULT_FROM_EMAIL in Django settings."
    )


def send_website_mail(
    *,
    subject: str,
    message: str,
    recipient_list: Iterable[str],
    website=None,
    html_message: Optional[str] = None,
    fail_silently: bool = False,
) -> bool:
    """Send a tenant-aware email using a resolved sender.

    Args:
        subject: Email subject.
        message: Plaintext body.
        recipient_list: Iterable of email addresses.
        website: Optional tenant to derive the sender address.
        html_message: Optional HTML body.
        fail_silently: If True, suppress exceptions from Django email.

    Returns:
        True if sending did not raise; False if an exception occurred.
    """
    from_email = get_website_sender_email(website)
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=list(recipient_list),
            fail_silently=fail_silently,
            html_message=html_message,
        )
        logger.info("Email sent from %s to %s", from_email, recipient_list)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Failed to send email to %s: %s",
            recipient_list,
            exc,
            exc_info=True,
        )
        return False


def send_priority_email(
    *,
    user,
    subject: str,
    message: str,
    website=None,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    context: Optional[dict] = None,
    html_message: Optional[str] = None,
    use_async: Optional[bool] = None,
) -> None:
    """Send an email with a priority-driven HTML skin.

    If `html_message` is not provided, this renders a template chosen by
    `priority` (see `get_template_for_priority`).

    Args:
        user: Recipient user (must have `.email`).
        subject: Email subject.
        message: Plaintext body (fallback and text part).
        website: Optional tenant to resolve sender address.
        priority: Notification priority for template selection.
        context: Extra template context.
        html_message: Optional pre-rendered HTML body.
        use_async: If True, dispatch via Celery task. If None, uses
            `settings.USE_ASYNC_EMAIL` as the default.

    Returns:
        None. Errors are logged.
    """
    if not getattr(user, "email", None):
        logger.warning("send_priority_email: user has no email; skipping.")
        return

    # Decide async at call-time or from settings.
    if use_async is None:
        use_async = bool(getattr(settings, "USE_ASYNC_EMAIL", False))

    if use_async:
        try:
            from notifications_system.tasks.notifications import (  # type: ignore
                async_send_website_mail,
            )
            async_send_website_mail.delay(
                user.id, subject, message, html_message, getattr(website, "id", None)
            )
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Async email fallback to sync due to error: %s", exc
            )

    # Render HTML if not provided.
    html = html_message
    if html is None:
        tpl = get_template_for_priority(priority)
        ctx = dict(context or {})
        ctx.update(
            {
                "user": user,
                "subject": subject,
                "message": message,
                "website_name": getattr(website, "name", "Our Platform"),
            }
        )
        html = render_to_string(tpl, ctx)

    from_email = get_website_sender_email(website)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[user.email],
        )
        email.attach_alternative(html, "text/html")
        email.send()
        logger.info("Priority email sent to %s (priority=%s)", user.email, priority)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Priority email failed to %s: %s", user.email, exc)