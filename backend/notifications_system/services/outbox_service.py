"""
Outbox service — the reliability layer between NotificationService
and the Celery task pipeline.

Responsibilities:
    - Deduplicate events via SHA-256 key
    - Write Outbox row in the caller's DB transaction
    - Queue the Celery task immediately after write
    - Requeue stale PENDING rows (called by beat worker)

The outbox pattern guarantees no notification is ever lost:
    If Celery is down when enqueue() runs
        → row stays PENDING
        → requeue_pending() picks it up within 5 minutes

    If the caller's DB transaction rolls back
        → outbox row rolls back with it
        → notification never fires for something that didn't happen

    If the same event fires twice concurrently
        → get_or_create with dedupe_key suppresses the duplicate
        → exactly one notification reaches the user

    If the beat worker is also down
        → row stays PENDING indefinitely
        → fires as soon as either worker or beat recovers
"""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from notifications_system.enums import (
    NotificationPriority,
    get_event_category,
)

logger = logging.getLogger(__name__)


class OutboxService:
    """
    Writes notification events to the outbox table and queues
    the Celery task to process them.

    Called exclusively by NotificationService — never by other apps.
    """

    @staticmethod
    def enqueue(
        *,
        event_key: str,
        recipient,
        website,
        context: Dict[str, Any],
        channels: List[str],
        priority: str = NotificationPriority.NORMAL,
        is_critical: bool = False,
        is_silent: bool = False,
        is_digest: bool = False,
        digest_group: str = '',
        triggered_by=None,
    ):
        """
        Write an event to the outbox and queue the Celery task.

        This method is safe to call inside any DB transaction —
        the outbox row is committed with the caller's transaction.
        If the transaction rolls back, the outbox row rolls back too.

        Args:
            event_key: Event key e.g. 'order.completed'
            recipient: User instance receiving the notification
            website: Website instance for tenancy scoping
            context: Template variables dict
            channels: Resolved delivery channels
            priority: NotificationPriority value
            is_critical: Bypasses mute and DND in dispatcher
            is_silent: Store record only — no delivery
            is_digest: Group into digest batch
            digest_group: Digest group key
            triggered_by: User who caused the event — None means system

        Returns:
            Outbox instance if created.
            None if deduplicated (same event already queued).
        """
        from notifications_system.models.outbox import Outbox

        payload = OutboxService._build_payload(
            context=context,
            channels=channels,
            priority=priority,
            is_critical=is_critical,
            is_silent=is_silent,
            is_digest=is_digest,
            digest_group=digest_group,
            triggered_by=triggered_by,
            event_key=event_key,
        )

        dedupe_key = OutboxService._build_dedupe_key(
            event_key=event_key,
            recipient_id=recipient.id,
            website_id=website.id,
        )

        outbox, created = Outbox.objects.get_or_create(
            dedupe_key=dedupe_key,
            defaults={
                'event_key': event_key,
                'user': recipient,
                'website': website,
                'payload': payload,
            },
        )

        if not created:
            logger.info(
                "OutboxService.enqueue() deduplicated: "
                "event=%s user=%s website=%s.",
                event_key,
                recipient.id,
                website.id,
            )
            return None

        OutboxService._queue_task(outbox.pk)

        logger.info(
            "OutboxService.enqueue() queued: "
            "outbox=%s event=%s user=%s website=%s.",
            outbox.pk,
            event_key,
            recipient.id,
            website.id,
        )
        return outbox

    @staticmethod
    def requeue_pending() -> int:
        """
        Requeue all PENDING outbox rows whose Celery task was
        never queued or whose retry time has passed.

        Called by the beat worker every 5 minutes as a safety net.
        Covers the case where Redis was briefly unavailable when
        enqueue() tried to queue the task.

        Returns:
            Count of rows requeued.
        """
        from notifications_system.models.outbox import Outbox

        pending = Outbox.objects.filter(
            status=Outbox.PENDING,
        ).filter(
            Q(next_retry_at__isnull=True) |
            Q(next_retry_at__lte=timezone.now())
        )

        count = 0
        for outbox in pending.iterator():
            OutboxService._queue_task(outbox.pk)
            count += 1

        if count:
            logger.info(
                "OutboxService.requeue_pending() requeued %s rows.",
                count,
            )

        return count

    # -------------------------
    # Private helpers
    # -------------------------

    @staticmethod
    def _build_payload(
        *,
        context: Dict[str, Any],
        channels: List[str],
        priority: str,
        is_critical: bool,
        is_silent: bool,
        is_digest: bool,
        digest_group: str,
        triggered_by,
        event_key: str,
    ) -> Dict[str, Any]:
        """
        Build the full payload dict stored on the Outbox row.

        This payload is everything the dispatcher needs to process
        the notification downstream — it is the complete handoff
        from the write side to the read side of the outbox pattern.

        Storing it on the Outbox row means the dispatcher is fully
        self-contained — it never needs to re-query NotificationService
        or re-resolve channels or priority.
        """
        return {
            'context': context,
            'channels': channels,
            'priority': priority,
            'is_critical': is_critical,
            'is_silent': is_silent,
            'is_digest': is_digest,
            'digest_group': digest_group,
            'triggered_by_id': getattr(triggered_by, 'id', None),
            'category': get_event_category(event_key),
        }

    @staticmethod
    def _build_dedupe_key(
        event_key: str,
        recipient_id: int,
        website_id: int,
    ) -> str:
        """
        Build a deterministic SHA-256 dedupe key.

        FIX: context is intentionally excluded from the key.
        Including context caused two problems:
          1. Slightly different context (e.g. a timestamp in the payload)
             would bypass deduplication entirely.
          2. Processed outbox rows with context in the key permanently
             blocked re-sending the same event (e.g. a second password
             reset hours later) even after the row was purged, because
             the context hash differed.

        Rate limiting in NotificationService handles burst protection.
        Outbox row purging (cleanup_processed_outbox) recycles keys
        so legitimate recurring sends work after the retention window.
        """
        raw = f"{event_key}:{recipient_id}:{website_id}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def _queue_task(outbox_id: int) -> None:
        """
        Queue the Celery task to process this outbox entry.

        Falls back gracefully if Celery is unavailable —
        requeue_pending() beat task will recover within 5 minutes.
        Never raises.
        """
        if not getattr(settings, 'ENABLE_CELERY', True):
            logger.info(
                "OutboxService._queue_task(): ENABLE_CELERY=False. "
                "Outbox %s will be processed by polling worker.",
                outbox_id,
            )
            return

        try:
            from notifications_system.tasks.send import process_outbox_entry
            process_outbox_entry.delay(outbox_id) # type: ignore[attr-defined]
            logger.debug(
                "OutboxService._queue_task(): queued task for outbox=%s.",
                outbox_id,
            )
        except Exception as exc:
            logger.warning(
                "OutboxService._queue_task(): Celery unavailable. "
                "Outbox %s will be requeued by beat worker. Error: %s",
                outbox_id,
                exc,
            )