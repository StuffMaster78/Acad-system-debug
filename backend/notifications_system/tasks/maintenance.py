# notifications_system/tasks/maintenance.py
"""
Maintenance tasks for the notification system.

Full Celery Beat schedule — add this block to your settings:

    from celery.schedules import crontab

    CELERY_BEAT_SCHEDULE = {
        'notif-clear-stale-digests': {
            'task': 'notifications_system.tasks.maintenance.clear_stale_digests',
            'schedule': crontab(hour=3, minute=0),
        },
        'notif-rebuild-unread-counts': {
            'task': 'notifications_system.tasks.maintenance.rebuild_unread_counts',
            'schedule': crontab(hour=4, minute=0),
        },
        'notif-cleanup-processed-outbox': {
            'task': 'notifications_system.tasks.maintenance.cleanup_processed_outbox',
            'schedule': crontab(hour=3, minute=30),
        },
        'notif-requeue-pending': {
            'task': 'notifications_system.tasks.maintenance.requeue_pending_outbox',
            'schedule': crontab(minute='*/5'),
        },
        'notif-expire-stale': {
            'task': 'notifications_system.tasks.maintenance.expire_stale_notifications',
            'schedule': crontab(minute='*/30'),
        },
        'notif-alert-dead-letters': {
            'task': 'notifications_system.tasks.maintenance.alert_dead_letter_outbox',
            'schedule': crontab(minute='*/15'),
        },
        'notif-process-webhook-events': {
            'task': 'notifications_system.tasks.maintenance.process_pending_webhook_events',
            'schedule': crontab(minute='*/5'),
        },
    }
"""
from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Existing tasks
# ─────────────────────────────────────────────────────────────

@shared_task
def clear_stale_digests(before_days: int = 30) -> None:
    """Delete sent digest rows older than before_days. Run daily."""
    from notifications_system.services.digest_service import DigestService
    deleted = DigestService.clear_stale_digests(before_days=before_days)
    logger.info("clear_stale_digests: deleted %s rows.", deleted)


@shared_task
def rebuild_unread_counts() -> None:
    """
    Recalculate unread counts from source of truth.
    Run daily or manually after data migrations if counts drift.
    """
    from notifications_system.models.user_notification_meta import (
        UserNotificationMeta,
    )
    from notifications_system.models.notifications_user_status import (
        NotificationsUserStatus,
    )

    metas = UserNotificationMeta.objects.select_related('user', 'website').all()
    updated = 0

    for meta in metas.iterator():
        actual_count = NotificationsUserStatus.objects.filter(
            user=meta.user,
            website=meta.website,
            is_read=False,
        ).count()

        if meta.unread_count != actual_count:
            meta.unread_count = actual_count
            meta.save(update_fields=['unread_count', 'updated_at'])
            updated += 1

    logger.info("rebuild_unread_counts: updated %s meta rows.", updated)


@shared_task
def cleanup_processed_outbox(before_days: int = 7) -> None:
    """
    Delete processed outbox rows older than before_days.

    Recycles dedupe_keys so the same event can be legitimately
    re-sent after the retention window. Override via OUTBOX_RETAIN_DAYS
    in settings. Run daily.
    """
    from django.conf import settings
    from notifications_system.models.outbox import Outbox

    before_days = getattr(settings, 'OUTBOX_RETAIN_DAYS', before_days)
    threshold = timezone.now() - timedelta(days=before_days)
    deleted, _ = Outbox.objects.filter(
        status=Outbox.PROCESSED,
        processed_at__lt=threshold,
    ).delete()
    logger.info("cleanup_processed_outbox: deleted %s rows.", deleted)


# ─────────────────────────────────────────────────────────────
# New tasks
# ─────────────────────────────────────────────────────────────

@shared_task(name='notifications_system.tasks.maintenance.requeue_pending_outbox')
def requeue_pending_outbox() -> None:
    """
    Requeue PENDING outbox rows whose Celery task was never queued.

    Safety net for when Redis/broker was briefly unavailable when
    OutboxService.enqueue() ran. Without this, those rows sit in
    PENDING forever and notifications are silently lost.

    Run every 5 minutes.
    """
    from notifications_system.services.outbox_service import OutboxService
    count = OutboxService.requeue_pending()
    if count:
        logger.info("requeue_pending_outbox: requeued %s rows.", count)


@shared_task(name='notifications_system.tasks.maintenance.expire_stale_notifications')
def expire_stale_notifications() -> None:
    """
    Mark sent in-app notifications as cancelled past their expires_at.

    Consolidated here from expiry.py so all scheduled tasks live in
    one place with a single Beat config. expiry.py remains as an alias
    for backwards compatibility with any existing Beat entries.

    Run every 30 minutes.
    """
    from notifications_system.models.notifications import Notification
    from notifications_system.enums import DeliveryStatus

    count = Notification.objects.filter(
        expires_at__lt=timezone.now(),
        status=DeliveryStatus.SENT,
    ).update(status=DeliveryStatus.CANCELLED)

    if count:
        logger.info(
            "expire_stale_notifications: expired %s notifications.", count
        )


@shared_task(name='notifications_system.tasks.maintenance.alert_dead_letter_outbox')
def alert_dead_letter_outbox() -> None:
    """
    Surface permanently-failed outbox entries to your alerting system.

    Logs WARNING per entry so Sentry / CloudWatch / Datadog picks them
    up. Extend to post to Slack or PagerDuty if needed.

    Run every 15 minutes.
    """
    from notifications_system.models.outbox import Outbox

    failed = Outbox.objects.filter(status=Outbox.FAILED).order_by('created_at')
    count = failed.count()

    if count == 0:
        return

    logger.warning(
        "DEAD LETTER ALERT: %s outbox entries have permanently failed "
        "and require manual review.",
        count,
    )

    for entry in failed[:50]:
        logger.warning(
            "Dead letter outbox: id=%s event=%s user=%s "
            "attempts=%s last_error=%r created=%s",
            entry.pk,
            entry.event_key,
            getattr(entry.user, 'id', None),
            entry.attempts,
            (entry.last_error or '')[:200],
            entry.created_at.isoformat(),
        )


@shared_task(name='notifications_system.tasks.maintenance.process_pending_webhook_events')
def process_pending_webhook_events() -> None:
    """
    Process ProviderWebhookEvent rows still in PENDING state.

    Webhook views process events immediately on receipt. This task
    catches any that failed during the original request so suppression
    events are never permanently lost.

    Run every 5 minutes.
    """
    try:
        from notifications_system.models.email_suppression import (
            EmailSuppression,
            ProviderWebhookEvent,
            SuppressionReason,
        )
    except ImportError:
        logger.warning(
            "process_pending_webhook_events: email_suppression models not "
            "found. Run makemigrations."
        )
        return

    SUPPRESS_TYPES = {
        'sendgrid': {'bounce', 'spamreport', 'unsubscribe', 'group_unsubscribe'},
        'ses':      {'bounce', 'complaint'},
        'mailgun':  {'bounced', 'complained', 'unsubscribed'},
    }

    pending = ProviderWebhookEvent.objects.filter(
        status=ProviderWebhookEvent.PENDING,
    ).order_by('received_at')[:200]

    processed = failed = ignored = 0

    for event in pending:
        suppress_types = SUPPRESS_TYPES.get(event.provider, set())

        if event.event_type not in suppress_types or not event.email:
            event.mark_ignored()
            ignored += 1
            continue

        try:
            EmailSuppression.suppress(
                email=event.email,
                reason=SuppressionReason.BOUNCE_HARD,
                provider=event.provider,
                provider_event_id=event.provider_event_id,
                raw_payload=event.raw_payload,
            )
            event.mark_processed()
            processed += 1
        except Exception as exc:
            event.mark_failed(str(exc))
            failed += 1
            logger.exception(
                "process_pending_webhook_events: failed id=%s: %s",
                event.pk,
                exc,
            )

    logger.info(
        "process_pending_webhook_events: "
        "processed=%s failed=%s ignored=%s.",
        processed,
        failed,
        ignored,
    )