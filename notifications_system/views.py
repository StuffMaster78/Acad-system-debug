from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer,
    NotificationMarkReadSerializer
)
from rest_framework import status as rest_status


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        """
        Return only the notifications for the current user.
        Supports optional filtering.
        """
        user = self.request.user
        queryset = Notification.objects.filter(user=user).order_by("-created_at")

        # Optional filters
        notif_type = self.request.query_params.get("type")
        category = self.request.query_params.get("category")
        unread = self.request.query_params.get("unread")

        if notif_type:
            queryset = queryset.filter(type=notif_type)
        if category:
            queryset = queryset.filter(category=category)
        if unread == "true":
            queryset = queryset.filter(is_read=False)

        return queryset

    @action(detail=False, methods=["post"])
    def mark_as_read(self, request):
        """
        Mark one or more notifications as read.
        
        Endpoint:
        `POST /api/notifications/mark_as_read/`
        
        This action accepts a list of notification IDs and marks them as read.

        Payload Example:
        {
            "ids": [1, 2, 3]
        }

        Returns:
        - HTTP 200: A count of how many notifications were marked as read
        - HTTP 400: If the request data is invalid
        """
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data["ids"]

        updated = Notification.objects.filter(
            user=request.user,
            id__in=ids,
            is_read=False
        ).update(is_read=True)

        return Response({"updated": updated}, status=rest_status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        """
        Mark all notifications for the authenticated user as read.
        """
        updated = Notification.objects.filter(
            user=self.request.user,
            is_read=False
        ).update(is_read=True)
        return Response(
            {"status": "success", "updated": updated},
            status=rest_status.HTTP_200_OK
        )


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification preferences.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer

    def get_queryset(self):
        """
        Filter preferences to the authenticated user.
        """
        return NotificationPreference.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Allow users to update their preferences.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)