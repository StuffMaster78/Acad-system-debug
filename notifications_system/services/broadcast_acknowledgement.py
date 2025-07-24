# notifications_system/services/broadcast_acknowledgement_service.py

from django.utils.timezone import now
from django.db.models import Q
from django.utils import timezone
from notifications_system.models.broadcast_notification import (
    BroadcastAcknowledgement
)

from notifications_system.models.broadcast_notification import (
    BroadcastNotification,
    BroadcastAcknowledgement
)
from websites.models import Website


class BroadcastAcknowledgementService:
    """Service for managing acknowledgements of broadcast notifications."""
    @staticmethod
    def acknowledge(user, broadcast, website, via_channel="in_app"):
        """
        Marks a broadcast as acknowledged by the user.
        """
        ack, created = BroadcastAcknowledgement.objects.get_or_create(
            user=user,
            broadcast=broadcast,
            website=website,
            defaults={
                "acknowledged_at": now(),
                "via_channel": via_channel
            }
        )
        return ack

    @staticmethod
    def has_acknowledged(user, broadcast):
        """
        Checks if a user has already acknowledged a broadcast.
        """
        return BroadcastAcknowledgement.objects.filter(
            user=user, broadcast=broadcast
        ).exists()

    @staticmethod
    def get_pending_acknowledgements(user, website):
        """
        Returns all active, blocking broadcasts that the user hasn't acknowledged.
        These must be shown to the user before proceeding in the dashboard.
        """
        all_broadcasts = BroadcastNotification.objects.filter(
            is_active=True,
            is_blocking=True,
            website=website,
        ).exclude(
            id__in=BroadcastAcknowledgement.objects.filter(user=user).values_list(
                "broadcast_id", flat=True
            )
        )
        return all_broadcasts

    @staticmethod
    def require_dashboard_access(user, website):
        """
        If any blocking broadcast is pending acknowledgment, return it.
        Otherwise, return None.
        Use this to block access to dashboard until acknowledged.
        """
        pending = BroadcastAcknowledgementService.get_pending_acknowledgements(
            user, website
        )
        return pending.first()  # Return one at a time for UI to display
    
    @staticmethod
    def get_user_broadcasts(user, website):
        acknowledged_ids = BroadcastAcknowledgement.objects.filter(
            user=user,
            broadcast__website=website,
        ).values_list("broadcast_id", flat=True)

        return BroadcastNotification.objects.filter(
            website=website,
            is_active=True
        ).exclude(id__in=acknowledged_ids).filter(
            Q(pinned=True) | Q(require_acknowledgement=True)
        ).order_by('-pinned', '-created_at')