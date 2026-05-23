"""
Automation Sequence Runner
============================

Processes automation enrollments: sends the next email in a sequence
when its delay period has elapsed.

Celery beat::

    "run-automation-sequences": {
        "task": "cms_newsletters.tasks.automation_runner.run_automation_sequences",
        "schedule": 3600,  # every hour
    }
"""

import logging

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@shared_task
def run_automation_sequences():
    """Process all active automation enrollments whose next_send_at has passed."""
    from cms_newsletters.models import (
        AutomationEnrollment,
        AutomationStep,
        NewsletterEvent,
    )

    now = timezone.now()

    due_enrollments = AutomationEnrollment.objects.filter(
        status="active",
        next_send_at__lte=now,
    ).select_related("subscriber", "sequence")

    sent = 0
    completed = 0
    errors = 0

    for enrollment in due_enrollments.iterator(chunk_size=50):
        try:
            # Get the current step
            step = AutomationStep.objects.filter(
                sequence=enrollment.sequence,
                step_order=enrollment.current_step,
                is_active=True,
            ).first()

            if not step:
                # No more active steps — mark as completed
                enrollment.status = "completed"
                enrollment.completed_at = now
                enrollment.save(update_fields=["status", "completed_at"])
                completed += 1
                continue

            # Send the email
            _send_automation_email(enrollment, step)
            sent += 1

            # Advance to next step
            next_step = AutomationStep.objects.filter(
                sequence=enrollment.sequence,
                step_order__gt=enrollment.current_step,
                is_active=True,
            ).order_by("step_order").first()

            if next_step:
                enrollment.current_step = next_step.step_order
                enrollment.next_send_at = now + timezone.timedelta(
                    days=next_step.delay_days
                )
                enrollment.save(update_fields=["current_step", "next_send_at"])
            else:
                enrollment.status = "completed"
                enrollment.completed_at = now
                enrollment.save(update_fields=["status", "completed_at"])
                completed += 1

        except Exception as exc:
            logger.error(
                "Automation step failed for enrollment %s: %s",
                enrollment.pk, exc,
            )
            errors += 1

    if sent or completed:
        logger.info(
            "Automation runner: %d emails sent, %d sequences completed, %d errors",
            sent, completed, errors,
        )
    return {"sent": sent, "completed": completed, "errors": errors}


@shared_task
def enroll_subscriber(subscriber_id: int, sequence_id: int):
    """Enroll a subscriber into an automation sequence.
    Called when a trigger event fires (e.g., email-gated attachment download)."""
    from cms_newsletters.models import (
        AutomationEnrollment,
        AutomationSequence,
        AutomationStep,
        Subscriber,
    )

    try:
        subscriber = Subscriber.objects.get(pk=subscriber_id)
        sequence = AutomationSequence.objects.get(pk=sequence_id, is_active=True)
    except (Subscriber.DoesNotExist, AutomationSequence.DoesNotExist) as exc:
        logger.warning("Enrollment failed: %s", exc)
        return {"error": str(exc)}

    # Check if already enrolled
    existing = AutomationEnrollment.objects.filter(
        subscriber=subscriber,
        sequence=sequence,
    ).first()

    if existing:
        if existing.status in ("active", "paused"):
            return {"skipped": True, "reason": "Already enrolled"}
        # If completed or cancelled, allow re-enrollment
        existing.delete()

    # Get first step
    first_step = AutomationStep.objects.filter(
        sequence=sequence,
        is_active=True,
    ).order_by("step_order").first()

    if not first_step:
        return {"error": "Sequence has no active steps"}

    enrollment = AutomationEnrollment.objects.create(
        subscriber=subscriber,
        sequence=sequence,
        current_step=first_step.step_order,
        next_send_at=timezone.now() + timezone.timedelta(
            days=first_step.delay_days
        ),
        status="active",
    )

    logger.info(
        "Enrolled %s in sequence '%s' (step %d, sends in %d days)",
        subscriber.email,
        sequence.name,
        first_step.step_order,
        first_step.delay_days,
    )
    return {"enrollment_id": enrollment.pk}


def _send_automation_email(enrollment, step):
    """Send a single automation step email."""
    subscriber = enrollment.subscriber
    sequence = enrollment.sequence
    site = sequence.site

    from_email = f"noreply@{site.hostname}"
    from_name = site.site_name

    # Render body
    body_html = ""
    if step.body:
        parts = []
        for block in step.body:
            if block.block_type == "paragraph":
                parts.append(f"<div>{block.value}</div>")
            elif block.block_type == "heading":
                value = block.value
                if isinstance(value, dict):
                    level = value.get("level", "h2")
                    text = value.get("text", "")
                    parts.append(f"<{level}>{text}</{level}>")
            elif block.block_type == "cta":
                value = block.value
                if isinstance(value, dict):
                    text = value.get("text", "Click here")
                    url = value.get("url", "#")
                    parts.append(
                        f'<p><a href="{url}" style="background:#007bff;'
                        f'color:#fff;padding:12px 24px;text-decoration:none;'
                        f'border-radius:4px;">{text}</a></p>'
                    )
            else:
                parts.append(f"<div>{block.value}</div>")
        body_html = "\n".join(parts)

    body_text = strip_tags(body_html)

    email = EmailMultiAlternatives(
        subject=step.subject_line,
        body=body_text,
        from_email=f"{from_name} <{from_email}>",
        to=[subscriber.email],
    )
    email.attach_alternative(body_html, "text/html")

    # Unsubscribe header
    unsubscribe_url = f"https://{site.hostname}/unsubscribe/{subscriber.pk}/"
    email.extra_headers["List-Unsubscribe"] = f"<{unsubscribe_url}>"
    email.extra_headers["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

    email.send(fail_silently=False)

    logger.debug(
        "Sent automation email '%s' to %s (sequence: %s, step: %d)",
        step.subject_line,
        subscriber.email,
        sequence.name,
        step.step_order,
    )
