from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from django.utils.timezone import now

from notifications_system.models import Notification, NotificationPreference
from notifications_system.serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    NotificationPriorityMetaSerializer
)
from notifications_system.utils.priority_mapper import (
    PRIORITY_LABEL_CHOICES
)

class NotificationThrottle(UserRateThrottle):
    rate = '60/min'  # customize as needed for bell spam prevention


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles listing and interacting with user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [NotificationThrottle]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            website=self.request.user.website
        ).order_by("-created_at")

    @action(detail=False, methods=["get"])
    def unread(self, request):
        qs = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return Response({"status": "marked as read"})

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        count = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({
            "status": "all marked as read",
            "updated": count
        })


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    Allow users to view and update their notification settings.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_object(self):
        obj, _ = NotificationPreference.objects.get_or_create(
            user=self.request.user,
            website=self.request.user.website
        )
        return obj

    def perform_update(self, serializer):
        serializer.save(user=self.request.user, website=self.request.user.website)



class NotificationMetaView(APIView):
    """
    Expose priority levels for dropdowns etc.
    """
    permission_classes = []  # Public or auth as needed

    def get(self, request, *args, **kwargs):
        priorities = [
            {"value": value, "label": label}
            for value, label in PRIORITY_LABEL_CHOICES
        ]
        return Response({
            "priorities": NotificationPriorityMetaSerializer(priorities, many=True).data
        })