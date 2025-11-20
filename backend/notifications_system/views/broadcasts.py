from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications_system.models.broadcast_notification import (
    BroadcastAcknowledgement, BroadcastNotification
)
from notifications_system.serializers import BroadcastNotificationSerializer
from notifications_system.services.broadcast_acknowledgement import (
    BroadcastAcknowledgementService
)


class BroadcastNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Broadcast notifications are sent to many users
    (e.g., system-wide announcements).
    """
    serializer_class = BroadcastNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BroadcastNotification.objects.filter(
            is_active=True,
            websites=self.request.user.website
        ).order_by("-created_at")

    @action(detail=False, methods=["get"], url_path="fetch-user-broadcasts")
    def fetch_user_broadcasts(self, request):
        """
        Get all broadcasts relevant to the authenticated user.
        """
        website = getattr(request.user, 'active_website', None)
        if not website:
            return Response({"detail": "Website context missing."}, status=400)

        broadcasts = BroadcastAcknowledgementService.get_user_broadcasts(
            user=request.user,
            website=website
        )
        serializer = self.get_serializer(broadcasts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="acknowledge")
    def acknowledge(self, request, pk=None):
        """
        Mark a broadcast as acknowledged by the user.
        """
        broadcast = self.get_object()
        BroadcastAcknowledgement.objects.get_or_create(
            user=request.user,
            broadcast=broadcast,
        )
        return Response({"detail": "Acknowledged."})
    


    """
    List all broadcast notifications: GET /broadcast-notifications/
    Retrieve a single broadcast: GET /broadcast-notifications/{id}/
    Get all broadcasts relevant to the user: GET /broadcast-notifications/fetch-user-broadcasts/
    Acknowledge a broadcast: POST /broadcast-notifications/{id}/acknowledge/
    """