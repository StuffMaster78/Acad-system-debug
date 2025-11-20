"""Manage user acknowledgements for broadcast notifications."""

from __future__ import annotations

from typing import Optional

from django.db.models import Q, QuerySet
from django.utils import timezone

from notifications_system.models.broadcast_notification import (
    BroadcastAcknowledgement,
    BroadcastNotification,
)


class BroadcastAcknowledgementService:
    """Service to record and query broadcast acknowledgements."""

    @staticmethod
    def acknowledge(
        user,
        broadcast: BroadcastNotification,
        website,
        *,
        via_channel: str = "in_app",
    ) -> BroadcastAcknowledgement:
        """Mark a broadcast as acknowledged by the user.

        Args:
            user: The acknowledging user.
            broadcast: The broadcast being acknowledged.
            website: Tenant/website context for the broadcast.
            via_channel: Channel used to show the broadcast (e.g., "in_app").

        Returns:
            The `BroadcastAcknowledgement` row.
        """
        ack, _ = BroadcastAcknowledgement.objects.get_or_create(
            user=user,
            broadcast=broadcast,
            website=website,
            defaults={
                "acknowledged_at": timezone.now(),
                "via_channel": via_channel,
            },
        )
        return ack

    @staticmethod
    def has_acknowledged(
        user,
        broadcast: BroadcastNotification,
    ) -> bool:
        """Check whether the user already acknowledged the broadcast.

        Args:
            user: The user to check.
            broadcast: The broadcast in question.

        Returns:
            True if acknowledged; False otherwise.
        """
        return BroadcastAcknowledgement.objects.filter(
            user=user, broadcast=broadcast
        ).exists()

    @staticmethod
    def get_pending_acknowledgements(
        user,
        website,
    ) -> QuerySet[BroadcastNotification]:
        """List blocking broadcasts the user must acknowledge.

        Args:
            user: The user to check.
            website: Tenant/website context.

        Returns:
            QuerySet of active, blocking broadcasts not yet acknowledged
            by the user.
        """
        acknowledged_ids = BroadcastAcknowledgement.objects.filter(
            user=user
        ).values_list("broadcast_id", flat=True)

        return BroadcastNotification.objects.filter(
            is_active=True,
            is_blocking=True,
            website=website,
        ).exclude(id__in=acknowledged_ids)

    @staticmethod
    def require_dashboard_access(
        user,
        website,
    ) -> Optional[BroadcastNotification]:
        """Return a pending blocking broadcast, if any.

        Use this to gate dashboard access until the user acknowledges.

        Args:
            user: The user to check.
            website: Tenant/website context.

        Returns:
            A single pending broadcast to show, or None if none pending.
        """
        pending = BroadcastAcknowledgementService.get_pending_acknowledgements(
            user, website
        )
        return pending.first()

    @staticmethod
    def get_user_broadcasts(
        user,
        website,
    ) -> QuerySet[BroadcastNotification]:
        """Get active broadcasts for the user that need attention.

        Includes pinned or require_acknowledgement broadcasts that the
        user has not yet acknowledged. Sorted by importance then recency.

        Args:
            user: The user to fetch for.
            website: Tenant/website context.

        Returns:
            QuerySet of broadcasts, ordered by pinned then created_at desc.
        """
        acknowledged_ids = BroadcastAcknowledgement.objects.filter(
            user=user,
            broadcast__website=website,
        ).values_list("broadcast_id", flat=True)

        return (
            BroadcastNotification.objects.filter(
                website=website,
                is_active=True,
            )
            .exclude(id__in=acknowledged_ids)
            .filter(Q(pinned=True) | Q(require_acknowledgement=True))
            .order_by("-pinned", "-created_at")
        )