from __future__ import annotations

import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string

from notifications_system.enums import NotificationPriority
from notifications_system.utils.email_templates import (
    get_template_for_priority,
)

logger = logging.getLogger(__name__)


def get_website_sender_email(website=None) -> str:
    """Resolve a sender email for the tenant/website.

    Args:
        website: Optional tenant object.

    Returns:
        Sender email string.

    Raises:
        ValueError: When no sender can be resolved.
    """
    if website and getattr(website, "no_reply_email", None):
        return website.no_reply_email

    if website and getattr(website, "domain", None):
        domain = website.domain.replace("https://", "").replace(
            "http://", ""
        ).strip("/")
        return f"no-reply@{domain}"

    default_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    if default_email:
        return default_email

    raise ValueError(
        "Missing sender email. Set Website.no_reply_email or "
        "DEFAULT_FROM_EMAIL."
    )


def send_website_mail(
    subject: str,
    message: str,
    recipient_list: list[str],
    *,
    website=None,
    html_message: str | None = None,
) -> bool:
    """Send an email using a tenant-aware sender.

    Args:
        subject: Email subject.
        message: Plain-text body.
        recipient_list: List of recipient emails.
        website: Optional tenant object.
        html_message: Optional HTML body.

    Returns:
        True on success, False on failure.
    """
    from_email = get_website_sender_email(website)

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=html_message,
        )
        logger.info("Email sent from %s to %s", from_email, recipient_list)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send email: %s", exc)
        return False


def send_priority_email(
    user,
    subject: str,
    message: str,
    *,
    html_message: str | None = None,
    context: dict | None = None,
    priority: int = NotificationPriority.NORMAL,
    website=None,
) -> None:
    """Send an email using a priority-based template.

    Args:
        user: Recipient user (must have .email).
        subject: Email subject line.
        message: Plain-text body.
        html_message: Explicit HTML override (optional).
        context: Extra template context (optional).
        priority: Priority enum value.
        website: Optional tenant object.
    """
    use_async = getattr(settings, "USE_ASYNC_EMAIL", False)
    if use_async:
        from notifications_system.tasks.notifications import (
            async_send_website_mail,
        )
        async_send_website_mail.delay(user.id, subject, message, html_message)
        return

    ctx = {"user": user, "subject": subject, "message": message}
    if context:
        ctx.update(context)

    template = get_template_for_priority(priority)
    html_content = html_message or render_to_string(template, ctx)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=(
                website.get_from_email() if website
                else getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com")  # noqa: E501
            ),
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as exc:  # noqa: BLE001
        logger.exception("Email failed to %s: %s", user.email, exc)