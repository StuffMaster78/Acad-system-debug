"""
Newsletter Send Task
======================

Sends scheduled newsletters when their send time arrives.
Handles A/B subject line splitting and event tracking.

Celery beat::

    "send-scheduled-newsletters": {
        "task": "cms_newsletters.tasks.send_newsletter.send_scheduled_newsletters",
        "schedule": 300,  # check every 5 minutes
    }
"""

import logging

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def send_scheduled_newsletters():
    """Find and send all newsletters whose scheduled_send_date has passed."""
    from cms_newsletters.models import Newsletter

    now = timezone.now()
    due = Newsletter.objects.filter(
        status="scheduled",
        scheduled_send_date__lte=now,
    )

    sent_count = 0
    for newsletter in due:
        try:
            newsletter.status = "sending"
            newsletter.save(update_fields=["status"])

            _send_newsletter(newsletter)

            newsletter.status = "sent"
            newsletter.sent_at = now
            newsletter.save(update_fields=["status", "sent_at"])
            sent_count += 1

        except Exception as exc:
            logger.error("Newsletter send failed for '%s': %s", newsletter.title, exc)
            newsletter.status = "failed"
            newsletter.save(update_fields=["status"])

    if sent_count:
        logger.info("Sent %d scheduled newsletters", sent_count)
    return {"sent": sent_count}


def _send_newsletter(newsletter):
    """Send a single newsletter to all eligible subscribers."""
    from cms_newsletters.models import (
        NewsletterAnalytics,
        NewsletterEvent,
        Subscriber,
    )

    subscribers = Subscriber.objects.filter(
        site=newsletter.site,
        is_active=True,
    )

    # Filter by category if set
    if newsletter.category:
        subscribers = subscribers.filter(categories=newsletter.category)

    total = subscribers.count()
    if total == 0:
        logger.info("No subscribers for newsletter '%s' — skipping", newsletter.title)
        return

    # A/B split
    has_ab = bool(newsletter.subject_line_b)
    split_point = int(total * (newsletter.ab_split_percentage / 100)) if has_ab else 0

    sent = 0
    bounced = 0

    for i, subscriber in enumerate(subscribers.iterator(chunk_size=100)):
        # Determine which subject variant
        if has_ab and i < split_point:
            subject = newsletter.subject_line_b
            variant = "B"
        else:
            subject = newsletter.subject_line
            variant = "A"

        try:
            _send_to_subscriber(newsletter, subscriber, subject, variant)
            NewsletterEvent.objects.create(
                newsletter=newsletter,
                subscriber=subscriber,
                event_type="delivered",
                subject_variant=variant,
            )
            sent += 1
        except Exception as exc:
            logger.warning(
                "Send failed for %s: %s", subscriber.email, exc,
            )
            NewsletterEvent.objects.create(
                newsletter=newsletter,
                subscriber=subscriber,
                event_type="bounced",
                subject_variant=variant,
            )
            bounced += 1

    # Create analytics summary
    NewsletterAnalytics.objects.update_or_create(
        newsletter=newsletter,
        defaults={
            "sent_count": sent + bounced,
            "delivered_count": sent,
            "bounce_count": bounced,
            "bounce_rate": (bounced / (sent + bounced) * 100) if (sent + bounced) > 0 else 0,
        },
    )

    logger.info(
        "Newsletter '%s' sent to %d subscribers (%d bounced)",
        newsletter.title, sent, bounced,
    )


def _send_to_subscriber(newsletter, subscriber, subject, variant):
    """Send a single email to a subscriber."""
    from_email = newsletter.sender_email or f"noreply@{newsletter.site.hostname}"
    from_name = newsletter.sender_name or newsletter.site.site_name

    # Render body from StreamField blocks to HTML
    body_html = _render_newsletter_body(newsletter)

    # Add tracking pixel
    body_html += (
        f'<img src="https://{newsletter.site.hostname}'
        f'/api/newsletter/track/open/{newsletter.pk}/{subscriber.pk}/" '
        f'width="1" height="1" style="display:none;" />'
    )

    # Plain text fallback
    from django.utils.html import strip_tags

    body_text = strip_tags(body_html)

    email = EmailMultiAlternatives(
        subject=subject,
        body=body_text,
        from_email=f"{from_name} <{from_email}>",
        to=[subscriber.email],
    )
    email.attach_alternative(body_html, "text/html")

    # Add unsubscribe header
    unsubscribe_url = (
        f"https://{newsletter.site.hostname}"
        f"/unsubscribe/{subscriber.pk}/"
    )
    email.extra_headers["List-Unsubscribe"] = f"<{unsubscribe_url}>"
    email.extra_headers["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

    email.send(fail_silently=False)


def _render_newsletter_body(newsletter) -> str:
    """Render StreamField blocks to HTML for email."""
    body = newsletter.body
    if not body:
        return ""

    parts = []
    for block in body:
        if block.block_type == "paragraph":
            parts.append(f"<div>{block.value}</div>")
        elif block.block_type == "heading":
            value = block.value
            if isinstance(value, dict):
                level = value.get("level", "h2")
                text = value.get("text", "")
                parts.append(f"<{level}>{text}</{level}>")
        elif block.block_type == "image":
            value = block.value
            if isinstance(value, dict):
                image = value.get("image")
                if image:
                    try:
                        url = image.get_rendition("width-600").url
                        alt = value.get("alt_text", "")
                        parts.append(
                            f'<img src="{url}" alt="{alt}" '
                            f'style="max-width:100%;height:auto;" />'
                        )
                    except Exception:
                        pass
        elif block.block_type == "cta":
            value = block.value
            if isinstance(value, dict):
                text = value.get("text", "Click here")
                url = value.get("url", "#")
                parts.append(
                    f'<p style="text-align:center;margin:20px 0;">'
                    f'<a href="{url}" style="background:#007bff;color:#fff;'
                    f'padding:12px 24px;text-decoration:none;border-radius:4px;">'
                    f'{text}</a></p>'
                )
        elif block.block_type == "divider":
            parts.append('<hr style="border:1px solid #eee;margin:20px 0;" />')
        else:
            # Fallback: render as text
            parts.append(f"<div>{block.value}</div>")

    return "\n".join(parts)