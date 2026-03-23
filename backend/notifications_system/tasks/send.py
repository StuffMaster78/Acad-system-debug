# notifications_system/tasks/send.py
"""
Core delivery tasks.
These are the Celery tasks that do the actual work after
NotificationService.notify() writes the outbox row.
"""
from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from notifications_system.enums import DeliveryStatus, NotificationChannel

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='notifications_system.tasks.send.process_outbox_entry',
)
def process_outbox_entry(self, outbox_id: int) -> None:
    """
    Pick up an outbox entry and dispatch to recipients.
    Called immediately after OutboxService.enqueue() writes the row.
    Retries up to 3 times with 60s delay on failure.
    """
    from django.contrib.auth import get_user_model
    from notifications_system.models.outbox import Outbox
    from notifications_system.services.dispatcher import NotificationDispatcher

    User = get_user_model()

    try:
        outbox = Outbox.objects.select_related('user', 'website').get(
            id=outbox_id
        )
    except Outbox.DoesNotExist:
        logger.warning(
            "process_outbox_entry: outbox=%s not found.",
            outbox_id,
        )
        return

    if not outbox.is_processable:
        logger.info(
            "process_outbox_entry: outbox=%s not processable status=%s.",
            outbox_id,
            outbox.status,
        )
        return

    try:
        payload = outbox.payload or {}

        # Resolve triggered_by user
        triggered_by = None
        triggered_by_id = payload.get('triggered_by_id')
        if triggered_by_id:
            try:
                triggered_by = User.objects.get(id=triggered_by_id)
            except User.DoesNotExist:
                logger.debug(
                    "process_outbox_entry: triggered_by_id=%s not found "
                    "for outbox=%s.",
                    triggered_by_id,
                    outbox_id,
                )

        NotificationDispatcher.dispatch(
            event_key=outbox.event_key,
            recipient=outbox.user,
            website=outbox.website,
            context=payload.get('context', {}),
            channels=payload.get('channels', []),
            triggered_by=triggered_by,
            priority=payload.get('priority', 'normal'),
            is_critical=payload.get('is_critical', False),
            is_silent=payload.get('is_silent', False),
            is_digest=payload.get('is_digest', False),
            digest_group=payload.get('digest_group', ''),
        )
        outbox.mark_processed()

        logger.info(
            "process_outbox_entry: outbox=%s processed successfully.",
            outbox_id,
        )

    except Exception as exc:
        logger.error(
            "process_outbox_entry: outbox=%s failed: %s.",
            outbox_id,
            exc,
        )
        outbox.mark_failed(error=str(exc))
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    name='notifications_system.tasks.send.send_channel_notification',
)
def send_channel_notification(self, delivery_id: int) -> None:
    """
    Render and deliver a single channel notification.

    Called by NotificationDispatcher._queue_channel_delivery()
    after a Delivery row has been created.

    Flow:
        1. Fetch Delivery row
        2. Cast channel string to NotificationChannel enum
        3. Guard — skip if terminal
        4. Resolve backend from BACKEND_MAP
        5. Call backend.send() → DeliveryResult
        6. Record attempt on Delivery model
        7. On success — update Notification status
        8. On failure — retry with backoff or attempt fallback
    """
    from notifications_system.models.delivery import Delivery
    from notifications_system.backends.email import EmailBackend
    from notifications_system.backends.in_app import InAppBackend

    BACKEND_MAP = {
        NotificationChannel.EMAIL:  EmailBackend,
        NotificationChannel.IN_APP: InAppBackend,
    }

    # ── Fetch ─────────────────────────────────────────────────
    try:
        delivery = Delivery.objects.select_related(
            'user', 'website', 'notification'
        ).get(id=delivery_id)
    except Delivery.DoesNotExist:
        logger.warning(
            "send_channel_notification: delivery=%s not found.",
            delivery_id,
        )
        return

    # ── Cast channel str → NotificationChannel ────────────────
    try:
        channel = NotificationChannel(delivery.channel)
    except ValueError:
        logger.error(
            "send_channel_notification: delivery=%s has unrecognised "
            "channel=%s.",
            delivery_id,
            delivery.channel,
        )
        delivery.record_attempt(
            success=False,
            error_code='INVALID_CHANNEL',
            error_detail=f"Unrecognised channel: {delivery.channel}",
        )
        return

    # ── Guard — skip terminal deliveries ──────────────────────
    if delivery.is_terminal:
        logger.info(
            "send_channel_notification: delivery=%s already terminal "
            "status=%s. Skipping.",
            delivery_id,
            delivery.status,
        )
        return

    # ── Resolve backend ───────────────────────────────────────
    backend_cls = BACKEND_MAP.get(channel)
    if not backend_cls:
        logger.error(
            "send_channel_notification: no backend for channel=%s "
            "delivery=%s.",
            channel,
            delivery_id,
        )
        delivery.record_attempt(
            success=False,
            error_code='NO_BACKEND',
            error_detail=f"No backend registered for channel: {channel}",
        )
        return

    # ── Deliver ───────────────────────────────────────────────
    backend = backend_cls(delivery)

    try:
        result = backend.send()
    except Exception as exc:
        logger.exception(
            "send_channel_notification: backend crashed "
            "delivery=%s channel=%s: %s.",
            delivery_id,
            channel,
            exc,
        )
        delivery.record_attempt(
            success=False,
            error_code='BACKEND_CRASH',
            error_detail=str(exc),
        )
        raise self.retry(exc=exc)

    # ── Record result ─────────────────────────────────────────
    delivery.record_attempt(
        success=result.success,
        provider_msg_id=result.provider_msg_id,
        error_code=result.error_code,
        error_detail=result.message if not result.success else '',
    )

    if result.success:
        logger.info(
            "send_channel_notification: delivery=%s channel=%s "
            "succeeded provider_msg_id=%s.",
            delivery_id,
            channel,
            result.provider_msg_id,
        )
        _update_notification_status(delivery.notification.id)

    else:
        logger.warning(
            "send_channel_notification: delivery=%s channel=%s "
            "failed error_code=%s.",
            delivery_id,
            channel,
            result.error_code,
        )
        if delivery.has_retries_remaining:
            raise self.retry(
                exc=Exception(result.message),
                countdown=_backoff_seconds(delivery.attempts),
            )
        _attempt_fallback(delivery)


@shared_task(
    bind=True,
    max_retries=1,
    default_retry_delay=30,
    name='notifications_system.tasks.send.process_broadcast_fanout',
)
def process_broadcast_fanout(self, broadcast_id: int) -> None:
    """
    Fan out a broadcast to all recipients.

    Called by BroadcastService._queue_fanout() after the
    BroadcastNotification row is written.

    Each recipient gets their own notify() call which writes
    its own outbox row — fully independent delivery per user.

    Retry once after 30 seconds on failure.
    """
    from notifications_system.services.broadcast_services import BroadcastService

    try:
        BroadcastService.fanout(broadcast_id)
    except Exception as exc:
        logger.error(
            "process_broadcast_fanout: broadcast=%s failed: %s.",
            broadcast_id,
            exc,
        )
        raise self.retry(exc=exc)


# ─────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────

def _update_notification_status(notification_id: int) -> None:
    """
    Check if all deliveries for a notification have settled
    and update the notification status accordingly.

    Called after each successful delivery. Only updates when
    all channels have reached a terminal state.
    """
    from notifications_system.models.delivery import Delivery
    from notifications_system.models.notifications import Notification

    has_pending = Delivery.objects.filter(
        notification_id=notification_id,
        status__in=[
            DeliveryStatus.PENDING,
            DeliveryStatus.QUEUED,
            DeliveryStatus.SENDING,
            DeliveryStatus.RETRYING,
        ],
    ).exists()

    if has_pending:
        return

    has_failed = Delivery.objects.filter(
        notification_id=notification_id,
        status=DeliveryStatus.FAILED,
    ).exists()

    final_status = DeliveryStatus.FAILED if has_failed else DeliveryStatus.SENT
    update_fields: dict = {'status': final_status}
    if not has_failed:
        update_fields['sent_at'] = timezone.now()

    Notification.objects.filter(id=notification_id).update(**update_fields)

    logger.info(
        "_update_notification_status: notification=%s → %s.",
        notification_id,
        final_status,
    )


def _attempt_fallback(delivery) -> None:
    """
    Queue delivery on the fallback channel if configured.
    Called when a channel has exhausted all retries and
    reached FAILED status.

    Does nothing if:
        - Delivery is not yet terminal
        - No fallback configured for this channel
        - Fallback is the same as the failed channel
        - Fallback channel already attempted for this notification
    """
    if not delivery.is_terminal:
        return

    # Look up fallback channel from website settings
    try:
        from notifications_system.models.notification_settings import (
            GlobalNotificationSystemSettings,
        )
        ws_settings = GlobalNotificationSystemSettings.for_website(
            delivery.website
        )
        fallback_channel = ws_settings.get_fallback_for_channel(
            delivery.channel
        )
    except Exception as exc:
        logger.debug(
            "_attempt_fallback: could not load settings "
            "for website=%s: %s.",
            getattr(delivery.website, 'pk', None),
            exc,
        )
        return

    if not fallback_channel:
        logger.debug(
            "_attempt_fallback: no fallback configured "
            "for channel=%s delivery=%s.",
            delivery.channel,
            delivery.pk,
        )
        return

    if fallback_channel == delivery.channel:
        return

    # Check we have not already tried this fallback
    from notifications_system.models.delivery import Delivery

    already_tried = Delivery.objects.filter(
        notification=delivery.notification,
        channel=fallback_channel,
    ).exists()

    if already_tried:
        logger.debug(
            "_attempt_fallback: fallback channel=%s already attempted "
            "for notification=%s. Skipping.",
            fallback_channel,
            delivery.notification_id,
        )
        return

    # Create fallback delivery row and queue its task
    fallback_delivery = Delivery.objects.create(
        event_key=delivery.event_key,
        user=delivery.user,
        website=delivery.website,
        notification=delivery.notification,
        channel=fallback_channel,
        priority=delivery.priority,
        payload=delivery.payload,
        rendered=delivery.rendered,
        triggered_by_fallback=True,
        status=DeliveryStatus.QUEUED,
    )

    send_channel_notification.delay(fallback_delivery.pk)  # type: ignore[attr-defined]

    logger.info(
        "_attempt_fallback: queued fallback delivery=%s "
        "channel=%s for original delivery=%s.",
        fallback_delivery.pk,
        fallback_channel,
        delivery.pk,
    )


def _backoff_seconds(attempts: int) -> int:
    """
    Exponential backoff capped at 10 minutes.

    attempts=1 → 2min
    attempts=2 → 4min
    attempts=3 → 8min
    """
    return min(2 ** attempts * 60, 600)