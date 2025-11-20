from __future__ import annotations

import logging
from typing import Optional

from celery import shared_task
from django.db import transaction


from notifications_system.models.notifications import Notification

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=0,   # backoff is scheduled by the caller; no Celery auto-retry
    rate_limit="20/s",  # tune for your infra
    acks_late=True,     # worker will re-deliver if it dies mid-task
    ignore_result=True,
)
def retry_delivery(
    self,
    *,
    notification_id: int,
    channel: str,
    attempt: int,
    email_override: Optional[str] = None,
    html_message: Optional[str] = None,
) -> None:
    """Retry a single-channel delivery for an existing notification.

    This task is scheduled by NotificationService._deliver(...) when a
    channel attempt fails and async retries are enabled.

    Args:
        notification_id: ID of the Notification row to deliver.
        channel: Delivery channel key (e.g., "email").
        attempt: Attempt number being executed (1-based).
        email_override: Optional override recipient for email.
        html_message: Optional pre-rendered HTML for backends.

    Returns:
        None. Delivery result is recorded by the service.
    """
    try:
        with transaction.atomic():
            try:
                note = (
                    Notification.objects
                    .select_for_update()
                    .get(id=notification_id)
                )
            except Notification.DoesNotExist:
                logger.warning(
                    "retry_delivery: notification %s no longer exists",
                    notification_id,
                )
                return

            # Guard: if the notification was already sent or canceled,
            # skip retry to avoid double-sends after operator actions.
            if getattr(note, "status", None) in {"canceled"}:
                logger.info(
                    "retry_delivery: notification %s is canceled; skip",
                    notification_id,
                )
                return

        # Call back into the service (centralized logging + fallbacks).
        from notifications_system.services.core import NotificationService
        NotificationService._deliver(  # noqa: SLF001 (internal on purpose)
            note,
            channel,
            html_message=html_message,
            email_override=email_override,
            attempt=attempt,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "retry_delivery task failed (note=%s, channel=%s, attempt=%s): %s",
            notification_id,
            channel,
            attempt,
            exc,
        )