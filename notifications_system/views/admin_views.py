from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action

from notifications_system.models.notifications import Notification
from notifications_system.serializers import NotificationSerializer
from notifications_system.filters import NotificationFilter
from django_filters.rest_framework import DjangoFilterBackend # type: ignore


class NotificationAdminViewSet(viewsets.ModelViewSet):
    """
    Admin CRUD access for all notifications across users/websites.
    """
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NotificationFilter

    @action(detail=False, methods=["get"], url_path="unread")
    def unread(self, request):
        """
        List all unread notifications (filtered via query params if provided).
        """
        qs = self.filter_queryset(self.get_queryset().filter(is_read=False))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a notification and return a JSON confirmation instead of empty 204.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"status": "deleted"})