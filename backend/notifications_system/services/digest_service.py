"""
notifications_system/services/digest_service.py

Manages notification digest grouping, scheduling, and delivery.
Digests group multiple notifications into a single periodic email
instead of sending each notification immediately.
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict, Iterable, List, Optional

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class DigestService:
    """
    Manages the full digest lifecycle:
    - Checking if an event is digest-eligible
    - Queuing digest rows when notifications are marked is_digest=True
    - Scheduling delivery times per frequency
    - Rendering and sending due digests
    - Cleaning up stale sent digests
    """

    # -------------------------
    # Eligibility checks
    # -------------------------

    @staticmethod
    def is_digest_eligible(event_key: str) -> bool:
        """
        Returns True if this event is configured as digest-eligible.
        Checks NotificationEventConfig.digest_eligible.
        """
        from notifications_system.models.event_config import NotificationEventConfig
        return NotificationEventConfig.objects.filter(
            event__event_key=event_key,
            digest_eligible=True,
            is_active=True,
        ).exists()

    @staticmethod
    def is_enabled_for_user(user, website) -> bool:
        """
        Returns True if the user has digest enabled on their preferences.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
        )
        try:
            pref = NotificationPreference.objects.get(
                user=user,
                website=website,
            )
            return pref.digest_enabled
        except NotificationPreference.DoesNotExist:
            return False

    @staticmethod
    def get_digest_frequency(user, website) -> str:
        """
        Returns the user's configured digest frequency.
        Falls back to daily if not set.
        """
        from notifications_system.models.notification_preferences import (
            NotificationPreference,
        )
        from notifications_system.enums import DigestFrequency
        try:
            pref = NotificationPreference.objects.get(
                user=user,
                website=website,
            )
            return pref.digest_frequency or DigestFrequency.DAILY
        except NotificationPreference.DoesNotExist:
            return DigestFrequency.DAILY

    # -------------------------
    # Queuing
    # -------------------------

    @staticmethod
    def queue_digest(
        user,
        website,
        event_key: str,
        payload: dict,
        digest_group: str = '',
    ) -> Optional[object]:
        """
        Queue a digest row for a user if digest is enabled.
        Called by the Dispatcher when is_digest=True on a notification.

        Returns:
            NotificationDigest instance or None if skipped.
        """
        from notifications_system.models.digest_notifications import (
            NotificationDigest,
        )
        from notifications_system.models.notification_event import NotificationEvent

        if not DigestService.is_digest_eligible(event_key):
            logger.debug(
                "queue_digest() skipped: event=%s not digest eligible.",
                event_key,
            )
            return None

        if not DigestService.is_enabled_for_user(user, website):
            logger.debug(
                "queue_digest() skipped: user=%s digest not enabled.",
                user.id,
            )
            return None

        event = NotificationEvent.objects.filter(
            event_key=event_key, is_active=True
        ).first()
        if not event:
            logger.warning(
                "queue_digest() skipped: unknown event_key=%s.", event_key
            )
            return None

        frequency = DigestService.get_digest_frequency(user, website)
        scheduled_for = DigestService.calculate_scheduled_time(
            timezone.now(), frequency
        )

        digest, created = NotificationDigest.objects.get_or_create(
            user=user,
            website=website,
            event_key=event_key,
            scheduled_for=scheduled_for,
            defaults={
                'event': event,
                'digest_group': digest_group or f"{event_key}.digest",
                'payload': payload,
                'is_sent': False,
            },
        )

        if not created:
            # Merge payload into existing digest row
            existing_payload = digest.payload or {}
            if isinstance(existing_payload, list):
                existing_payload.append(payload)
            else:
                existing_payload = [existing_payload, payload]
            digest.payload = existing_payload
            digest.save(update_fields=['payload', 'updated_at'])

        return digest

    @staticmethod
    def calculate_scheduled_time(now, frequency: str):
        """
        Calculate next delivery time for a given frequency.
        All digests deliver at 08:00 local time.

        Args:
            now:       Current timezone-aware datetime
            frequency: DigestFrequency value

        Returns:
            datetime for next digest run
        """
        from notifications_system.enums import DigestFrequency

        base = now.replace(hour=8, minute=0, second=0, microsecond=0)

        if frequency == DigestFrequency.WEEKLY:
            days = (7 - now.weekday()) % 7
            days = 7 if days == 0 and now >= base else days
            return base + timedelta(days=days)

        if frequency == DigestFrequency.HOURLY:
            next_hour = now.replace(minute=0, second=0, microsecond=0)
            return next_hour + timedelta(hours=1)

        if frequency == DigestFrequency.MONTHLY:
            # First day of next month at 08:00
            if now.month == 12:
                return base.replace(year=now.year + 1, month=1, day=1)
            return base.replace(month=now.month + 1, day=1)

        # Default: daily at 08:00
        return base if now < base else base + timedelta(days=1)

    # -------------------------
    # Sending
    # -------------------------

    @staticmethod
    def send_due_digests() -> None:
        """
        Process and send all due unsent digests.
        Grouped by user to send one email per user per run.
        Called by the Celery beat task.
        """
        from notifications_system.models.digest_notifications import (
            NotificationDigest,
        )

        now = timezone.now()
        due = (
            NotificationDigest.objects.filter(
                is_sent=False,
                scheduled_for__lte=now,
            )
            .select_related('user', 'website')
            .order_by('user_id', 'scheduled_for')
        )

        grouped: Dict[int, List] = {}
        for digest in due:
            grouped.setdefault(digest.user_id, []).append(digest)

        for user_id, digests in grouped.items():
            DigestService._send_user_digest(user_id, digests)

    @staticmethod
    def _send_user_digest(user_id: int, digests: List) -> None:
        """
        Render and send a single user's digest email.
        Marks all included digest rows as sent on success.
        """
        from notifications_system.services.email_service import EmailService
        from notifications_system.services.template_service import TemplateService
        from notifications_system.enums import NotificationChannel
        from notifications_system.models.digest_notifications import (
            NotificationDigest,
        )

        User = settings.AUTH_USER_MODEL

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            logger.warning(
                "_send_user_digest() user not found: user_id=%s.", user_id
            )
            return

        if not user.email or not user.is_active:
            logger.info(
                "_send_user_digest() skipped: user=%s no email or inactive.",
                user_id,
            )
            return

        website = digests[0].website

        # Resolve digest template
        template = TemplateService.resolve(
            event_key='scheduled.digest_daily',
            channel=NotificationChannel.EMAIL,
            website=website,
        )
        if not template:
            logger.warning(
                "_send_user_digest() no template: user=%s website=%s.",
                user_id,
                website.id if website else None,
            )
            return

        # Build context from all digest payloads
        context = {
            'user_name': user.get_full_name() or user.username,
            'digest_count': len(digests),
            'items': [
                {
                    'event_key': d.event_key,
                    'payload': d.payload,
                    'scheduled_for': d.scheduled_for.isoformat(),
                }
                for d in digests
            ],
            'website_name': website.name if website else '',
        }

        rendered = TemplateService.render(template, context)

        try:
            EmailService.send_rendered(
                to_email=user.email,
                rendered=rendered,
                website=website,
            )

            # Mark all included digests as sent
            digest_ids = [d.id for d in digests]
            NotificationDigest.objects.filter(id__in=digest_ids).update(
                is_sent=True,
                sent_at=timezone.now(),
            )

            logger.info(
                "_send_user_digest() sent: user=%s digest_count=%s.",
                user_id,
                len(digests),
            )

        except Exception as exc:
            logger.error(
                "_send_user_digest() failed: user=%s error=%s.",
                user_id,
                exc,
            )

    # -------------------------
    # Maintenance
    # -------------------------

    @staticmethod
    def clear_stale_digests(before_days: int = 30) -> int:
        """
        Delete sent digest rows older than before_days.
        Returns count of deleted rows.
        Called by maintenance task.
        """
        from notifications_system.models.digest_notifications import (
            NotificationDigest,
        )

        threshold = timezone.now() - timedelta(days=before_days)
        deleted, _ = NotificationDigest.objects.filter(
            is_sent=True,
            scheduled_for__lt=threshold,
        ).delete()

        logger.info(
            "clear_stale_digests() deleted %s rows older than %s days.",
            deleted,
            before_days,
        )
        return deleted

    @staticmethod
    def preview_digest(user, website) -> Optional[str]:
        """
        Return rendered HTML preview of pending digest for a user.
        Does not send — for admin preview use only.
        """
        from notifications_system.models.digest_notifications import (
            NotificationDigest,
        )
        from notifications_system.services.template_service import TemplateService
        from notifications_system.enums import NotificationChannel

        pending = NotificationDigest.objects.filter(
            user=user,
            website=website,
            is_sent=False,
            scheduled_for__lte=timezone.now(),
        ).order_by('scheduled_for')

        if not pending.exists():
            return None

        template = TemplateService.resolve(
            event_key='scheduled.digest_daily',
            channel=NotificationChannel.EMAIL,
            website=website,
        )
        if not template:
            return None

        context = {
            'user_name': user.get_full_name() or user.username,
            'digest_count': pending.count(),
            'items': [
                {
                    'event_key': d.event_key,
                    'payload': d.payload,
                }
                for d in pending
            ],
        }

        rendered = TemplateService.render(template, context)
        return rendered.get('body_html', '')