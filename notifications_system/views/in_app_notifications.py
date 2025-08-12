from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications_system.models.notifications import Notification
from notifications_system.serializers import NotificationSerializer
from notifications_system.utils.in_app_helpers import get_user_notifications


class InAppNotificationViewSet(viewsets.ViewSet):
    """Handles in-app notifications for users."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List in-app notifications with sorting & optional website filter.
        """
        website = request.query_params.get("website")
        limit = int(request.query_params.get("limit", 50))
        offset = int(request.query_params.get("offset", 0))
        notifs = get_user_notifications(request.user, website, limit, offset)
        return Response(NotificationSerializer(notifs, many=True).data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = Notification.objects.filter(
            user=request.user, read=False, type="in_app"
        ).count()
        return Response({"unread_count": count})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notif = Notification.objects.filter(user=request.user, id=pk).first()
        if notif:
            notif.read = True
            notif.save(update_fields=["read"])
            return Response({"status": "marked as read"})
        return Response({"error": "Not found"}, status=404)

    @action(detail=True, methods=["post"])
    def toggle_pin(self, request, pk=None):
        notif = Notification.objects.filter(user=request.user, id=pk).first()
        if notif:
            notif.pinned = not notif.pinned
            notif.save(update_fields=["pinned"])
            return Response({"status": "pinned" if notif.pinned else "unpinned"})
        return Response({"error": "Not found"}, status=404)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        updated = Notification.objects.filter(
            user=request.user, read=False, type="in_app"
        ).update(read=True)
        return Response({"marked": updated})