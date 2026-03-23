"""
Broadcast notification endpoints — user-facing.
"""
from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications_system.models.broadcast_notification import BroadcastNotification
from notifications_system.serializers import BroadcastNotificationSerializer
from notifications_system.services.broadcast_acknowledgement import (
    BroadcastAcknowledgementService,
)


class BroadcastViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User-facing broadcast endpoints.
    Users view active broadcasts and acknowledge them.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BroadcastNotificationSerializer

    def get_queryset(self):
        user = self.request.user
        website = getattr(user, 'website', None)
        return BroadcastAcknowledgementService.get_user_broadcasts(
            user, website
        )

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge a broadcast notification."""
        website = getattr(request.user, 'website', None)
        try:
            broadcast = BroadcastNotification.objects.get(
                id=pk, website=website, is_active=True,
            )
        except BroadcastNotification.DoesNotExist:
            return Response(
                {'error': 'Broadcast not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        ack = BroadcastAcknowledgementService.acknowledge(
            user=request.user,
            broadcast=broadcast,
            website=website,
            via_channel=request.data.get('via_channel', 'in_app'),
        )
        return Response({
            'acknowledged': True,
            'acknowledged_at': ack.acknowledged_at.isoformat(),
        })

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Return broadcasts requiring acknowledgement."""
        website = getattr(request.user, 'website', None)
        pending = BroadcastAcknowledgementService.get_pending_acknowledgements(
            request.user, website
        )
        return Response(
            self.get_serializer(pending, many=True).data
        )

    @action(detail=False, methods=['get'])
    def blocking(self, request):
        """
        Return the next blocking broadcast the user must acknowledge.
        Vue uses this to gate dashboard access.
        Returns {blocking: false} if none pending.
        """
        website = getattr(request.user, 'website', None)
        broadcast = BroadcastAcknowledgementService.require_dashboard_access(
            request.user, website
        )
        if not broadcast:
            return Response({'blocking': False})
        return Response({
            'blocking': True,
            'broadcast': self.get_serializer(broadcast).data,
        })