from __future__ import annotations

import logging

from celery import shared_task

from users.selectors.profile_reminder_selector import list_users_missing_phone
from users.services.profile_reminder_service import ProfileReminderService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_missing_phone_reminders(self) -> dict[str, int]:
    """
    Send missing-phone reminders to eligible users.
    """
    checked = 0
    sent = 0
    skipped = 0
    failed = 0

    for user in list_users_missing_phone().iterator():
        checked += 1

        try:
            reminder = ProfileReminderService.send_missing_phone_reminder(
                user=user,
            )

            if reminder.status == "sent":
                sent += 1
            elif reminder.status == "skipped":
                skipped += 1
            else:
                failed += 1

        except Exception as exc:
            failed += 1
            logger.exception(
                "Failed to process missing-phone reminder for user_id=%s: %s",
                user.pk,
                str(exc),
            )

    return {
        "checked": checked,
        "sent": sent,
        "skipped": skipped,
        "failed": failed,
    }