from __future__ import annotations

import logging

from django.dispatch import receiver

from writer_compensation.signals import (
    adjustment_event_created,
    fine_event_created,
    payout_record_held,
    payout_record_paid,
    window_processing_started,
)

logger = logging.getLogger(__name__)


def _writer_user(writer_profile):
    return getattr(writer_profile, "user", None) or writer_profile.account_profile.user


@receiver(window_processing_started)
def on_window_processing_started(sender, window, **kwargs):
    """
    Window → PROCESSING.
    Notifies every writer who has at least one event in this window.
    """
    from writer_compensation.models.compensation_event import CompensationEvent
    from notifications_system.services.notification_service import NotificationService

    writers = (
        CompensationEvent.objects
        .filter(payment_window=window)
        .select_related("writer__account_profile__user")
        .values_list("writer__account_profile__user", flat=True)
        .distinct()
    )

    # Fetch the User instances — NotificationService requires User, not ID.
    from django.contrib.auth import get_user_model
    User = get_user_model()
    recipients = User.objects.filter(pk__in=writers, is_active=True)

    context = {
        "window_label": f"{window.start_date} - {window.end_date}",
        "start_date": str(window.start_date),
        "end_date": str(window.end_date),
        "window_id": window.pk,
    }

    for recipient in recipients:
        try:
            NotificationService.notify(
                event_key="compensation.payment_processing",
                recipient=recipient,
                website=window.website,
                context=context,
            )
        except Exception:
            logger.exception(
                "Failed to send compensation.payment_processing | "
                "user %s | window %s", recipient.pk, window.pk,
            )


@receiver(payout_record_paid)
def on_payout_record_paid(sender, record, **kwargs):
    """
    PayoutRecord → PAID.
    Notifies the individual writer with their payout amount and window.
    """
    from notifications_system.services.notification_service import NotificationService

    window = record.batch.payment_window
    writer_user = _writer_user(record.writer)

    try:
        NotificationService.notify(
            event_key="compensation.payment_paid",
            recipient=writer_user,
            website=window.website,
            context={
                "amount": str(record.total_amount),
                "window_label": f"{window.start_date} - {window.end_date}",
                "window_id": window.pk,
                "record_id": record.pk,
            },
        )
    except Exception:
        logger.exception(
            "Failed to send compensation.payment_paid | "
            "user %s | record %s", writer_user.pk, record.pk,
        )


@receiver(payout_record_held)
def on_payout_record_held(sender, record, **kwargs):
    """
    PayoutRecord → HELD.
    Generic message only — hold_reason is NEVER sent to the writer.
    """
    from notifications_system.services.notification_service import NotificationService

    window = record.batch.payment_window
    writer_user = _writer_user(record.writer)

    try:
        NotificationService.notify(
            event_key="compensation.payment_on_hold",
            recipient=writer_user,
            website=window.website,
            context={
                "window_label": f"{window.start_date} - {window.end_date}",
                "window_id": window.pk,
                # hold_reason intentionally excluded
            },
        )
    except Exception:
        logger.exception(
            "Failed to send compensation.payment_on_hold | "
            "user %s | record %s", writer_user.pk, record.pk,
        )


@receiver(fine_event_created)
def on_fine_event_created(sender, event, **kwargs):
    """
    FINE CompensationEvent created.
    Notifies the writer with amount and source.
    """
    from notifications_system.services.notification_service import NotificationService

    source_label = (
        f"{event.source_type.replace('_', ' ').title()} #{event.source_id}"
        if event.source_type and event.source_id
        else "your account"
    )

    try:
        NotificationService.notify(
            event_key="compensation.fine_applied",
            recipient=event.writer.user,
            website=event.website,
            context={
                "amount": str(abs(event.amount)),
                "source_label": source_label,
                "source_type": event.source_type,
                "source_id": event.source_id,
                "event_id": event.pk,
            },
        )
    except Exception:
        logger.exception(
            "Failed to send compensation.fine_applied | "
            "user %s | event %s", event.writer.user.pk, event.pk,
        )


@receiver(adjustment_event_created)
def on_adjustment_event_created(sender, event, **kwargs):
    """
    ADJUSTMENT CompensationEvent created.
    Amount can be positive (credit) or negative (deduction).
    """
    from notifications_system.services.notification_service import NotificationService

    try:
        NotificationService.notify(
            event_key="compensation.adjustment_applied",
            recipient=event.writer.user,
            website=event.website,
            context={
                "amount": str(abs(event.amount)),
                "direction": "credit" if event.amount > 0 else "deduction",
                "event_id": event.pk,
            },
        )
    except Exception:
        logger.exception(
            "Failed to send compensation.adjustment_applied | "
            "user %s | event %s", event.writer.user.pk, event.pk,
        )
