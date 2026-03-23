# notifications_system/services/broadcast_acknowledgement.py
"""
Records and queries user acknowledgements for broadcast notifications.
"""
from __future__ import annotations

import logging
from typing import Optional

from django.core.cache import cache
from django.db.models import Q, QuerySet
from django.utils import timezone

from notifications_system.enums import NotificationChannel
from notifications_system.models.broadcast_notification import (
    BroadcastAcknowledgement,
    BroadcastNotification,
    BroadcastOverride,
)

logger = logging.getLogger(__name__)


def _is_visible_to_user(                    # ← module-level, not inside class
    broadcast: BroadcastNotification,
    user,
    user_role: Optional[str],
    override_broadcast_ids: Optional[set] = None,
) -> bool:
    """
    Determine if a broadcast should be visible to this user.

    Visibility rules (any one match = visible):
        1. show_to_all=True          → visible to everyone
        2. target_roles contains     → visible to that role
           the user's role
        3. BroadcastOverride exists  → explicit per-user override
           for this user with is_active=True

    Args:
        broadcast:              BroadcastNotification instance
        user:                   User instance
        user_role:              User's role string, may be None
        override_broadcast_ids: Pre-fetched set of broadcast IDs
                                the user has an active override for.
                                Pass this to avoid N+1 queries when
                                calling inside a loop.

    Returns:
        True if the user should see this broadcast
    """
    # Rule 1 — show to everyone
    if broadcast.show_to_all:
        return True

    # Rule 2 — role-based targeting
    target_roles = broadcast.target_roles or []
    if user_role and user_role in target_roles:
        return True

    # Rule 3 — explicit per-user override
    if override_broadcast_ids is not None:
        return broadcast.pk in override_broadcast_ids

    # Fallback single query when no prefetch provided
    return BroadcastOverride.objects.filter(
        broadcast=broadcast,
        user=user,
        is_active=True,
    ).exists()


def _prefetch_override_ids(user, qs: QuerySet) -> set:
    """
    Pre-fetch all broadcast IDs in qs that have an active
    BroadcastOverride for this user.

    Turns O(N) override queries into a single query.
    """
    return set(
        BroadcastOverride.objects.filter(
            user=user,
            is_active=True,
            broadcast__in=qs,
        ).values_list('broadcast_id', flat=True)
    )


class BroadcastAcknowledgementService:
    """Records and queries broadcast acknowledgements."""

    @staticmethod
    def acknowledge(
        user,
        broadcast: BroadcastNotification,
        website,
        via_channel: str = NotificationChannel.IN_APP,
    ) -> BroadcastAcknowledgement:
        """
        Mark a broadcast as acknowledged by the user.
        Idempotent — calling twice returns the existing row.

        Args:
            user:        The acknowledging user
            broadcast:   The broadcast being acknowledged
            website:     Tenant context
            via_channel: Channel through which the user saw the broadcast

        Returns:
            BroadcastAcknowledgement instance
        """
        ack, created = BroadcastAcknowledgement.objects.get_or_create(
            user=user,
            broadcast=broadcast,
            defaults={
                'website': website,
                'acknowledged_at': timezone.now(),
                'via_channel': via_channel,
            },
        )

        if created:
            # Invalidate the dashboard gate cache for this user
            cache.delete(
                f'broadcast_blocking:{getattr(website, "pk", None)}:{user.pk}'
            )
            logger.info(
                "BroadcastAcknowledgementService.acknowledge: "
                "user=%s broadcast=%s via=%s.",
                user.pk,
                broadcast.pk,
                via_channel,
            )

        return ack

    @staticmethod
    def has_acknowledged(
        user,
        broadcast: BroadcastNotification,
    ) -> bool:
        """Return True if the user has already acknowledged this broadcast."""
        return BroadcastAcknowledgement.objects.filter(
            user=user,
            broadcast=broadcast,
        ).exists()

    @staticmethod
    def revoke(
        user,
        broadcast: BroadcastNotification,
    ) -> bool:
        """
        Remove a user's acknowledgement for a broadcast.
        Used when a broadcast is updated and must be re-acknowledged.

        Returns:
            True if an acknowledgement was deleted, False if none existed.
        """
        deleted, _ = BroadcastAcknowledgement.objects.filter(
            user=user,
            broadcast=broadcast,
        ).delete()

        if deleted:
            cache.delete(
                f'broadcast_blocking:'
                f'{getattr(broadcast.website, "pk", None)}:{user.pk}'
            )

        return bool(deleted)

    @staticmethod
    def revoke_all(broadcast: BroadcastNotification) -> int:
        """
        Remove all acknowledgements for a broadcast.
        Used when a broadcast is updated significantly and
        all users must re-acknowledge.

        Returns:
            Count of deleted acknowledgements.
        """
        deleted, _ = BroadcastAcknowledgement.objects.filter(
            broadcast=broadcast,
        ).delete()

        logger.info(
            "BroadcastAcknowledgementService.revoke_all: "
            "broadcast=%s deleted=%s acknowledgements.",
            broadcast.pk,
            deleted,
        )

        return deleted

    @staticmethod
    def get_pending_acknowledgements(
        user,
        website,
    ) -> QuerySet:
        """
        Return active blocking broadcasts the user must acknowledge.
        Excludes expired broadcasts and already-acknowledged ones.
        """
        now = timezone.now()
        acknowledged_ids = BroadcastAcknowledgement.objects.filter(
            user=user,
        ).values_list('broadcast_id', flat=True)

        return (
            BroadcastNotification.objects.filter(
                is_active=True,
                is_blocking=True,
                website=website,
            )
            .filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            )
            .exclude(id__in=acknowledged_ids)
            .order_by('-pinned', '-created_at')
        )

    @staticmethod
    def require_dashboard_access(
        user,
        website,
    ) -> Optional[BroadcastNotification]:
        """
        Return the next blocking broadcast the user must acknowledge
        before accessing the dashboard.

        Returns None if no blocking broadcasts are pending.

        Called by:
            - BroadcastViewSet.blocking() every 30s poll
            - Vue router guard before each navigation

        Logic:
            1. Find all active blocking broadcasts for this website
               that target this user (via role or show_to_all)
            2. Exclude any the user has already acknowledged
            3. Return the oldest unacknowledged one (FIFO)
               so users work through them in order

        Args:
            user:    Authenticated user instance
            website: Website instance for tenant scoping

        Returns:
            BroadcastNotification instance or None
        """
        website_pk = getattr(website, 'pk', None)
        cache_key = f'broadcast_blocking:{website_pk}:{user.pk}'

        # Short-circuit if cached — called every 30 seconds
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        acknowledged_ids = BroadcastAcknowledgement.objects.filter(
            user=user,
            broadcast__website=website,
        ).values_list('broadcast_id', flat=True)

        now = timezone.now()
        qs = BroadcastNotification.objects.filter(
            website=website,
            is_active=True,
            is_blocking=True,
            require_acknowledgement=True,
            sent_at__isnull=False,
        ).exclude(
            id__in=acknowledged_ids,
        ).exclude(
            expires_at__lt=now,
        ).order_by('sent_at')

        if not qs.exists():
            cache.set(cache_key, None, timeout=30)
            return None

        # Prefetch overrides to avoid N+1
        override_ids = _prefetch_override_ids(user, qs)
        user_role = getattr(user, 'role', None)

        visible_ids = [
            b.pk for b in qs
            if _is_visible_to_user(b, user, user_role, override_ids)
        ]

        if not visible_ids:
            cache.set(cache_key, None, timeout=30)
            return None

        result = qs.filter(pk__in=visible_ids).order_by('sent_at').first()
        cache.set(cache_key, result, timeout=30)
        return result

    @staticmethod
    def get_user_broadcasts(
        user,
        website,
    ) -> QuerySet:
        """
        Return active broadcasts visible to this user.
        Excludes acknowledged and expired broadcasts.
        Ordered by pinned status then recency.
        """
        now = timezone.now()
        acknowledged_ids = BroadcastAcknowledgement.objects.filter(
            user=user,
            broadcast__website=website,
        ).values_list('broadcast_id', flat=True)

        qs = (
            BroadcastNotification.objects.filter(
                website=website,
                is_active=True,
            )
            .filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            )
            .exclude(id__in=acknowledged_ids)
            .filter(
                Q(pinned=True) | Q(require_acknowledgement=True)
            )
            .order_by('-pinned', '-created_at')
        )

        # Prefetch overrides to avoid N+1
        override_ids = _prefetch_override_ids(user, qs)
        user_role = getattr(user, 'role', None)

        visible_ids = [
            b.pk for b in qs
            if _is_visible_to_user(b, user, user_role, override_ids)
        ]

        return qs.filter(pk__in=visible_ids)

    @staticmethod
    def get_acknowledgement_count(
        broadcast: BroadcastNotification,
    ) -> int:
        """Return how many users have acknowledged this broadcast."""
        return BroadcastAcknowledgement.objects.filter(
            broadcast=broadcast,
        ).count()