# =============================================================================
# writer_compensation/tasks/window_tasks.py
#
# Celery tasks for automated window lifecycle management.
#
# Schedule (set in celery beat):
# check_and_close_windows — runs at 23:50 every night
# check_and_open_windows — runs at 00:05 every night
# alert_pending_events — runs at 09:00 every day
# =============================================================================

from __future__ import annotations

import logging
from datetime import date, timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from writer_compensation.enums.compensation_enums import WindowStatus, WindowType
from writer_compensation.models.payment_window import PaymentWindow
from writer_compensation.services.window_service import WindowService

logger = logging.getLogger(__name__)


@shared_task(
    name="writer_compensation.tasks.check_and_close_windows",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def check_and_close_windows(self):
    """
    Runs at 23:50 every night.

    Finds every OPEN window whose end_date is today and closes it.
    Auto-confirms all pending events before closing so nothing is
    excluded from the batch.

    Creates the PayoutBatch and PayoutRecords automatically.
    Does NOT start processing — admin still controls that step.
    """
    today = date.today()
    windows_to_close = PaymentWindow.objects.filter(
        status=WindowStatus.OPEN,
        end_date=today,
        is_active=True,
    ).select_related("website")

    closed_count = 0
    for window in windows_to_close:
        try:
            with transaction.atomic():
                pending_count = _count_pending_events(window)
                WindowService.close_window(
                    window,
                    closed_by=None, # system-initiated
                    auto_confirm_pending=True, # never exclude events at auto-close
                )
                logger.info(
                    "Auto-closed window %s | site %s | pending auto-confirmed: %s",
                    window.pk, window.website.pk, pending_count,
                )
                closed_count += 1
        except Exception as exc:
            logger.error(
                "Failed to auto-close window %s | site %s | error: %s",
                window.pk, window.website.pk, exc,
            )
            # Retry the task if something unexpected happened.
            self.retry(exc=exc)

    logger.info("check_and_close_windows complete | closed: %s", closed_count)
    return {"closed": closed_count}


@shared_task(
    name="writer_compensation.tasks.check_and_open_windows",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def check_and_open_windows(self):
    """
    Runs at 00:05 every night.

    For every website that has an active payout preference, checks whether
    an OPEN window exists for today. If not, creates one automatically
    based on the site's configured cycle type.

    This guarantees there is always an open window available so
    EventIntakeService.record() never raises NoOpenWindowError in
    normal operation.
    """
    today = date.today()
    created_ids = []
    skipped_ids = []

    # Get all websites that have at least one active window (indicates they
    # are using the compensation system).
    active_website_ids = (
        PaymentWindow.objects
        .filter(is_active=True)
        .values_list("website_id", flat=True)
        .distinct()
    )

    for website_id in active_website_ids:
        try:
            already_open = PaymentWindow.objects.filter(
                website_id=website_id,
                status=WindowStatus.OPEN,
                is_active=True,
            ).exists()

            if already_open:
                skipped_ids.append(website_id)
                continue

            # Find the most recently closed window to determine cycle type
            # and compute the next window dates.
            last_window = (
                PaymentWindow.objects
                .filter(website_id=website_id, is_active=True)
                .order_by("-end_date")
                .first()
            )

            if last_window:
                cycle_type = last_window.cycle_type
                start_date = last_window.end_date + timedelta(days=1)
            else:
                # First window ever for this site — start today, biweekly default.
                cycle_type = WindowType.BIWEEKLY
                start_date = today

            end_date = _compute_end_date(start_date, cycle_type)

            from websites.models.websites import Website
            website = Website.objects.get(pk=website_id)

            WindowService.create_window(
                website=website,
                cycle_type=cycle_type,
                start_date=start_date,
                end_date=end_date,
                title=_generate_title(start_date, end_date, cycle_type),
                created_by=None, # system-initiated
            )
            created_ids.append(website_id)
            logger.info(
                "Auto-opened window | site %s | %s → %s | cycle: %s",
                website_id, start_date, end_date, cycle_type,
            )

        except Exception as exc:
            logger.error(
                "Failed to auto-open window | site %s | error: %s",
                website_id, exc,
            )
            self.retry(exc=exc)

    logger.info(
        "check_and_open_windows complete | created: %s | skipped (already open): %s",
        len(created_ids), len(skipped_ids),
    )
    return {"created": len(created_ids), "skipped": len(skipped_ids)}


@shared_task(name="writer_compensation.tasks.alert_pending_events")
def alert_pending_events():
    """
    Runs at 09:00 every day.

    Finds CLOSED windows that still have PENDING_CONFIRMATION events
    (events that were excluded from the batch) and logs/alerts so
    admin knows to create post-close adjustments if needed.
    """
    from writer_compensation.enums.compensation_enums import EventStatus
    from writer_compensation.models.compensation_event import CompensationEvent

    closed_windows_with_pending = (
        PaymentWindow.objects
        .filter(status=WindowStatus.CLOSED)
        .filter(
            events__status=EventStatus.PENDING_CONFIRMATION,
        )
        .distinct()
    )

    alerts = []
    for window in closed_windows_with_pending:
        count = CompensationEvent.objects.filter(
            payment_window=window,
            status=EventStatus.PENDING_CONFIRMATION,
        ).count()
        alerts.append({
            "window_id": window.pk,
            "website_id": window.website.pk,
            "count": count,
            "window": str(window),
        })
        logger.warning(
            "Closed window %s has %s unresolved PENDING_CONFIRMATION events",
            window.pk, count,
        )

    return {"alerts": alerts}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _count_pending_events(window: PaymentWindow) -> int:
    from writer_compensation.enums.compensation_enums import EventStatus
    from writer_compensation.models.compensation_event import CompensationEvent
    return CompensationEvent.objects.filter(
        payment_window=window,
        status=EventStatus.PENDING_CONFIRMATION,
    ).count()


def _compute_end_date(start_date: date, cycle_type: str) -> date:
    if cycle_type == WindowType.BIWEEKLY:
        return start_date + timedelta(days=13) # 14-day window
    else:
        # Monthly: last day of the same month as start_date.
        import calendar
        last_day = calendar.monthrange(start_date.year, start_date.month)[1]
        return date(start_date.year, start_date.month, last_day)


def _generate_title(start_date: date, end_date: date, cycle_type: str) -> str:
    cycle_label = "Bi-weekly" if cycle_type == WindowType.BIWEEKLY else "Monthly"
    return f"{cycle_label} {start_date.strftime('%b %d')} – {end_date.strftime('%b %d, %Y')}"