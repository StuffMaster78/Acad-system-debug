# notifications_system/services/dispatcher.py
"""
Picks up outbox entries and dispatches per-channel deliveries.
Called by the Celery task after NotificationService writes the outbox.

Responsibilities:
    - Check mute, DND, and cooldown via PreferenceService
    - Create Notification record
    - Create NotificationsUserStatus record
    - Per channel: check preferences, resolve template,
      render, create Delivery row, queue send task

Does NOT:
    - Write to the outbox (OutboxService)
    - Validate input (NotificationService)
    - Render templates directly (TemplateService)
    - Send emails or in-app messages (backends)
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.utils import timezone

from notifications_system.enums import (
    DeliveryStatus,
    NotificationPriority,
    get_event_category,
)

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    """
    Processes an outbox entry end-to-end.

    Creates the Notification record, checks preferences per channel,
    renders templates, creates Delivery rows, and queues send tasks.

    Called exclusively by process_outbox_entry Celery task.
    """

    @staticmethod
    def dispatch(
        *,
        event_key: str,
        recipient,
        website,
        context: Dict[str, Any],
        channels: List[str],
        triggered_by=None,
        priority: str = NotificationPriority.NORMAL,
        is_critical: bool = False,
        is_silent: bool = False,
        is_digest: bool = False,
        digest_group: str = '',
    ) -> Optional[object]:
        """
        Main dispatch entry point — called by process_outbox_entry task.

        Checks suppression conditions first — if any apply the
        notification is not created. Otherwise creates the Notification
        and NotificationsUserStatus records atomically, then queues
        per-channel delivery tasks.

        Args:
            event_key:    Event key e.g. 'order.completed'
            recipient:    User receiving the notification
            website:      Website instance for tenant scoping
            context:      Template context variables
            channels:     Channels resolved by NotificationService
            triggered_by: User who caused the event — None means system
            priority:     NotificationPriority value
            is_critical:  If True bypasses mute, DND, and cooldown
            is_silent:    Create record only — skip all delivery
            is_digest:    Group into digest batch — skip immediate delivery
            digest_group: Digest group key e.g. 'daily_summary'

        Returns:
            Notification instance if created.
            None if suppressed by mute, DND, or cooldown.
        """
        from notifications_system.services.preference_service import PreferenceService

        # --- Suppression checks — skip if critical
        if not is_critical:

            if PreferenceService.is_muted(recipient, website):
                logger.info(
                    "dispatch() suppressed — muted: "
                    "user=%s event=%s.",
                    recipient.id,
                    event_key,
                )
                return None

            if PreferenceService.is_in_dnd(recipient, website):
                logger.info(
                    "dispatch() suppressed — DND: "
                    "user=%s event=%s.",
                    recipient.id,
                    event_key,
                )
                return None

            if PreferenceService.is_on_cooldown(recipient, website, event_key):
                logger.info(
                    "dispatch() suppressed — cooldown: "
                    "user=%s event=%s.",
                    recipient.id,
                    event_key,
                )
                return None

        # --- Create Notification + NotificationsUserStatus atomically
        # Both rows are created together — if either fails neither persists.
        # The NotificationsUserStatus row is the per-user read/pin/ack state.
        from notifications_system.models.notifications import Notification
        from notifications_system.models.notifications_user_status import (
            NotificationsUserStatus,
        )

        with transaction.atomic():
            notification = Notification.objects.create(
                user=recipient,
                website=website,
                event_key=event_key,
                channels=channels,
                payload=context,
                actor=triggered_by,
                priority=priority,
                category=get_event_category(event_key),
                is_critical=is_critical,
                is_silent=is_silent,
                is_digest=is_digest,
                digest_group=digest_group,
                status=DeliveryStatus.PENDING,
            )

            NotificationsUserStatus.objects.create(
                user=recipient,
                website=website,
                notification=notification,
                priority=priority,
            )

        logger.info(
            "dispatch() created notification=%s event=%s "
            "user=%s website=%s channels=%s.",
            notification.id,
            event_key,
            recipient.id,
            website.id,
            channels,
        )

        # --- Silent — record only, no delivery
        if is_silent:
            logger.info(
                "dispatch() silent: notification=%s "
                "stored but not delivered.",
                notification.id,
            )
            return notification

        # --- Digest — queue for batch delivery, not immediate
        if is_digest:
            from notifications_system.services.digest_service import DigestService
            DigestService.queue_digest(
                user=recipient,
                website=website,
                event_key=event_key,
                payload=context,
                notification=notification,
                digest_group=digest_group,
            )
            logger.info(
                "dispatch() digest: notification=%s "
                "queued for digest group=%s.",
                notification.id,
                digest_group,
            )
            return notification

        # --- Per-channel delivery
        delivered_to_any = False
        for channel in channels:

            # Check per-channel user preference
            if not PreferenceService.should_notify(
                recipient, website, event_key, channel
            ):
                logger.info(
                    "dispatch() channel=%s skipped by preferences: "
                    "user=%s event=%s.",
                    channel,
                    recipient.id,
                    event_key,
                )
                continue

            NotificationDispatcher._queue_channel_delivery(
                notification=notification,
                channel=channel,
                context=context,
                priority=priority,
            )
            delivered_to_any = True

        # If every channel was suppressed by preferences
        # mark notification as cancelled so it does not
        # sit in PENDING forever
        if not delivered_to_any:
            Notification.objects.filter(id=notification.id).update(
                status=DeliveryStatus.CANCELLED,
            )
            logger.info(
                "dispatch() all channels suppressed: "
                "notification=%s marked CANCELLED.",
                notification.id,
            )

        return notification

    @staticmethod
    def _queue_channel_delivery(
        *,
        notification,
        channel: str,
        context: Dict[str, Any],
        priority: str,
    ) -> None:
        """
        Resolve template, render, create Delivery row, queue send task.

        One call per channel per notification.
        If the template is missing the channel is skipped and
        logged — delivery continues on remaining channels.

        Args:
            notification: Parent Notification instance
            channel:      Channel string e.g. 'email', 'in_app'
            context:      Template context variables
            priority:     Delivery priority
        """
        from notifications_system.models.delivery import Delivery
        from notifications_system.services.template_service import TemplateService

        # --- Resolve template
        template = TemplateService.resolve(
            event_key=notification.event_key,
            channel=channel,
            website=notification.website,
        )

        if not template:
            logger.warning(
                "_queue_channel_delivery() no template: "
                "event=%s channel=%s website=%s. "
                "Run validate_templates to find missing templates.",
                notification.event_key,
                channel,
                notification.website_id,
            )
            return

        # --- Render
        rendered = TemplateService.render(template, context)

        # --- Store rendered content on Notification for the first channel
        # Subsequent channels write their own rendered content to
        # their Delivery row — the Notification only needs one copy
        # for display purposes (typically the in-app rendering)
        if not notification.rendered:
            notification.rendered = rendered
            notification.save(update_fields=['rendered', 'updated_at'])

        # --- Create Delivery row
        # One row per channel — channel is a CharField not a list
        delivery = Delivery.objects.create(
            event_key=notification.event_key,
            user=notification.user,
            website=notification.website,
            notification=notification,
            channel=channel,              # single string — not a list
            priority=priority,
            payload=context,
            rendered=rendered,
            status=DeliveryStatus.QUEUED,
        )

        # --- Queue send task
        from notifications_system.tasks.send import send_channel_notification
        send_channel_notification.delay(delivery.id)

        logger.info(
            "_queue_channel_delivery() queued: "
            "delivery=%s channel=%s notification=%s.",
            delivery.id,
            channel,
            notification.id,
        )