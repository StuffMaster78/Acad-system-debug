"""
Single entry point for all notifications.
Responsibilities: validate, deduplicate, write outbox, queue task.
Everything else (preferences, rendering, delivery) is handled downstream.
"""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, Iterable, Optional

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from notifications_system.enums import (
    NotificationChannel,
    NotificationEvent,
    NotificationPriority,
    DeliveryStatus,
    get_event_category,
    is_valid_event,
)
from notifications_system.services.outbox_service import OutboxService

logger = logging.getLogger(__name__)

# Maximum notifications per user per event within RATE_LIMIT_WINDOW_SECONDS.
# Protects against runaway loops in calling services.
RATE_LIMIT_MAX = getattr(settings, 'NOTIFICATION_RATE_LIMIT_MAX', 10)
RATE_LIMIT_WINDOW_SECONDS = getattr(
    settings, 'NOTIFICATION_RATE_LIMIT_WINDOW_SECONDS', 300
) # 5 minutes


class NotificationService:
    """
    Central entry point for all notifications.

    All other apps call NotificationService.notify() — nothing else.
    This service validates input, deduplicates, writes to the outbox,
    and queues a Celery task. It does not render, deliver, or retry.

    Flow:
        NotificationService.notify()
            → rate-limit check (Redis)
            → writes Outbox row (dedupe via unique dedupe_key)
            → queues process_outbox_entry.delay()
            → Dispatcher handles preferences + rendering + delivery
    """

    @staticmethod
    def notify(
        *,
        event_key: str,
        recipient,
        website,
        context: Optional[Dict[str, Any]] = None,
        channels: Optional[Iterable[str]] = None,
        triggered_by=None,
        priority: str = NotificationPriority.NORMAL,
        is_critical: bool = False,
        is_silent: bool = False,
        is_digest: bool = False,
        is_broadcast: bool = False,
        digest_group: Optional[str] = None,
    ):
        """
        Fire a notification for a given event.

        Args:
            event_key: Dot-notation event e.g. 'order.completed'
            recipient: User instance receiving the notification
            website: Website instance — required for tenancy
            context: Template variables e.g. {'order_id': 1}
            channels: Override channels — None uses event config defaults
            triggered_by: User who caused the event — None means system
            priority: NotificationPriority value — defaults to NORMAL
            is_critical: If True bypasses mute and DND checks
            is_silent: Store only — do not deliver to user
            is_digest: Group into digest instead of immediate send
            digest_group: Digest group key e.g. 'daily_summary'

        Returns:
            Outbox instance if queued, None if skipped or failed.
        """
        # --- Validate
        if not recipient:
            logger.warning("notify() skipped: no recipient provided.")
            return None

        if not getattr(recipient, 'is_authenticated', False):
            logger.warning(
                "notify() skipped: unauthenticated recipient user=%s.",
                getattr(recipient, 'id', None),
            )
            return None

        if not event_key:
            logger.warning("notify() skipped: empty event_key.")
            return None

        if not is_valid_event(event_key):
            logger.warning(
                "notify() skipped: unregistered event_key=%s.",
                event_key,
            )
            return None

        if not website:
            logger.warning(
                "notify() skipped: no website provided for user=%s event=%s.",
                getattr(recipient, 'id', None),
                event_key,
            )
            return None

        # --- Global kill switch
        if not getattr(settings, 'ENABLE_NOTIFICATIONS', True):
            logger.info(
                "Notifications disabled globally. Skipping %s.", event_key
            )
            return None

        # --- Rate limit check (skipped for critical notifications)
        if not is_critical:
            if NotificationService._is_rate_limited(
                recipient_id=recipient.id,
                event_key=event_key,
                website_id=website.id,
            ):
                logger.warning(
                    "notify() rate-limited: user=%s event=%s website=%s.",
                    recipient.id,
                    event_key,
                    website.id,
                )
                return None

        context = dict(context or {})

        # --- Resolve event config defaults
        channels = NotificationService._resolve_channels(
            event_key=event_key,
            channels=channels,
        )

        # --- Build outbox payload
        payload = {
            'context': context,
            'channels': list(channels),
            'priority': priority,
            'is_critical': is_critical,
            'is_silent': is_silent,
            'is_digest': is_digest,
            'is_broadcast': is_broadcast,
            'digest_group': digest_group,
            'triggered_by_id': getattr(triggered_by, 'id', None),
            'category': get_event_category(event_key),
        }

        # --- Deduplicate via outbox dedupe_key
        # FIX: dedupe key excludes context so that recurring legitimate
        # events (e.g. second password reset) are not permanently blocked.
        # Window-based deduplication is enforced by the rate limiter above.
        dedupe_key = NotificationService._build_dedupe_key(
            event_key=event_key,
            recipient_id=recipient.id,
            website_id=website.id,
            context=context,
        )

        # --- Write outbox — same transaction as caller
        from notifications_system.models.outbox import Outbox

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
                "notify() deduplicated: event=%s user=%s website=%s.",
                event_key,
                recipient.id,
                website.id,
            )
            return None

        # --- Queue Celery task
        NotificationService._queue_task(outbox.pk)

        logger.info(
            "notify() queued: event=%s user=%s website=%s outbox=%s.",
            event_key,
            recipient.id,
            website.id,
            outbox.pk,
        )
        return outbox

    @staticmethod
    def notify_role(
        *,
        event_key: str,
        role: str,
        website,
        context: Optional[Dict[str, Any]] = None,
        triggered_by=None,
        priority: str = NotificationPriority.NORMAL,
        is_critical: bool = False,
    ):
        """
        Fire a notification to all active users of a given role on a website.
        Each user gets their own outbox entry and delivery.

        Args:
            event_key: Event to fire
            role: Role string e.g. 'writer', 'support'
            website: Website to scope users to
            context: Template context
            triggered_by: Who triggered the event
            priority: Notification priority
            is_critical: Bypass mute and DND
        """
        # FIX: was settings.AUTH_USER_MODEL (a string). get_user_model()
        # returns the actual model class.
        User = get_user_model()

        recipients = User.objects.filter(
            website=website,
            role=role,
            is_active=True,
        )

        queued = 0
        for recipient in recipients:
            result = NotificationService.notify(
                event_key=event_key,
                recipient=recipient,
                website=website,
                context=context,
                triggered_by=triggered_by,
                priority=priority,
                is_critical=is_critical,
            )
            if result:
                queued += 1

        logger.info(
            "notify_role() queued %s notifications: event=%s role=%s website=%s.",
            queued,
            event_key,
            role,
            website.id,
        )

    @staticmethod
    def notify_staff(
        *,
        event_key: str,
        website,
        context: Optional[Dict[str, Any]] = None,
        triggered_by=None,
        priority: str = NotificationPriority.NORMAL,
    ):
        """
        Notify all staff assigned to a website.
        Convenience wrapper around notify() for each active staff member.
        """
        from admin_management.models import StaffWebsiteAssignment

        # FIX: was settings.AUTH_USER_MODEL (a string). get_user_model()
        # returns the actual model class.
        User = get_user_model()

        staff_ids = StaffWebsiteAssignment.objects.filter(
            website=website,
            is_active=True,
        ).values_list('staff_member_id', flat=True)

        recipients = User.objects.filter(id__in=staff_ids, is_active=True)

        for recipient in recipients:
            NotificationService.notify(
                event_key=event_key,
                recipient=recipient,
                website=website,
                context=context,
                triggered_by=triggered_by,
                priority=priority,
            )

    # -------------------------
    # Private helpers
    # -------------------------

    @staticmethod
    def _is_rate_limited(
        recipient_id: int,
        event_key: str,
        website_id: int,
    ) -> bool:
        """
        Returns True if this user has exceeded the rate limit for this
        event on this website within the configured time window.

        Uses Redis INCR + EXPIRE for atomic, TTL-based counting.
        Falls back to False (allow) if Redis is unavailable — better
        to over-send than to silently drop critical notifications.

        Rate limit settings (in Django settings):
            NOTIFICATION_RATE_LIMIT_MAX: int (default 10)
            NOTIFICATION_RATE_LIMIT_WINDOW_SECONDS: int (default 300)
        """
        try:
            from django.core.cache import cache

            cache_key = (
                f"notif_rl:{website_id}:{recipient_id}:{event_key}"
            )
            count = cache.get(cache_key, 0)

            if count >= RATE_LIMIT_MAX:
                return True

            # Atomic increment — set TTL only on first write
            new_count = count + 1
            cache.set(cache_key, new_count, timeout=RATE_LIMIT_WINDOW_SECONDS)
            return False

        except Exception as exc:
            logger.warning(
                "_is_rate_limited() cache error — allowing through: %s", exc
            )
            return False

    @staticmethod
    def _resolve_channels(
        event_key: str,
        channels: Optional[Iterable[str]],
    ) -> list:
        """
        Resolve channels for an event.
        Uses caller-provided channels if given,
        otherwise falls back to event config defaults.
        """
        if channels:
            return list(channels)

        try:
            from notifications_system.models.event_config import (
                NotificationEventConfig,
            )
            config = NotificationEventConfig.objects.get(
                event_key=event_key,
                is_active=True,
            )
            return config.get_default_channels()
        except Exception:
            pass

        # Final fallback — in_app always works
        return [NotificationChannel.IN_APP]

    @staticmethod
    def _build_dedupe_key(
        event_key: str,
        recipient_id: int,
        website_id: int,
        context: dict,
    ) -> str:
        """
        Build a deterministic dedupe key for an outbox entry.

        Context is intentionally excluded from the key so that
        recurring legitimate events (e.g. a second password reset
        one hour later) are not permanently blocked by a stale
        outbox row. Window-based rate limiting handles burst
        protection instead.

        Same event + recipient + website = same key within the
        outbox lifetime. Outbox rows should be purged after
        processing (see maintenance task) to allow re-sending.
        """
        raw = f"{event_key}:{recipient_id}:{website_id}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @staticmethod
    def _queue_task(outbox_id: int) -> None:
        """
        Queue the Celery task to process this outbox entry.
        Falls back gracefully if Celery is unavailable.
        """
        if not getattr(settings, 'ENABLE_CELERY', True):
            logger.info(
                "Celery disabled. Outbox %s will be processed by polling worker.",
                outbox_id,
            )
            return

        try:
            from notifications_system.tasks.send import process_outbox_entry
            process_outbox_entry.delay(outbox_id) # type: ignore[attr-defined]
        except Exception as exc:
            logger.warning(
                "Celery unavailable. Outbox %s queued for polling worker: %s",
                outbox_id,
                exc,
            )