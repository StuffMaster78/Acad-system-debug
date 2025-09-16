from __future__ import annotations
from typing import Iterable

from django.db.models import Prefetch, Q
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications_system.models.notifications import Notification
from notifications_system.models.notifications_user_status import NotificationsUserStatus
from notifications_system.enums import NotificationType

from notifications_system.serializers import (
    NotificationFeedItemSerializer,
    NotificationStatusMarkSerializer,
    NotificationStatusBulkMarkSerializer,
)


class NotificationFeedViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    GET /api/notifications/feed/  -> user's in-app feed (with per-user state)
    """
    serializer_class = NotificationFeedItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = (
            NotificationsUserStatus.objects
            .select_related("notification", "notification__website", "notification__actor")
            .filter(user=user, notification__type=NotificationType.IN_APP)
        )

        # Optional filters
        is_read = self.request.query_params.get("is_read")
        if is_read in ("true", "false"):
            qs = qs.filter(is_read=(is_read == "true"))

        pinned = self.request.query_params.get("pinned")
        if pinned in ("true", "false"):
            qs = qs.filter(pinned=(pinned == "true"))

        website_id = self.request.query_params.get("website")
        if website_id:
            qs = qs.filter(notification__website_id=website_id)

        event = self.request.query_params.get("event")
        if event:
            qs = qs.filter(notification__event__icontains=event)

        # Sort: pinned first, then priority, then newest
        # If your priority is int (lower = more important), sort ascending
        return qs.order_by("-pinned", "priority", "-notification__created_at")

    @action(detail=False, methods=["post"], url_path="bulk-mark")
    def bulk_mark(self, request):
        """
        POST /api/notifications/feed/bulk-mark/
        {
          "ids": [status_id, ...]   # OR "all_unread": true
          "read": true|false|null,
          "pinned": true|false|null,
          "acknowledged": true|false|null
        }
        """
        ser = NotificationStatusBulkMarkSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = request.user
        data = ser.validated_data

        qs = NotificationsUserStatus.objects.filter(
            user=user, notification__type=NotificationType.IN_APP
        )

        if data.get("ids"):
            qs = qs.filter(id__in=data["ids"])
        elif data.get("all_unread"):
            qs = qs.filter(is_read=False)

        update_fields: dict = {}
        if data.get("read") is True:
            update_fields["is_read"] = True
        if data.get("pinned") is True:
            update_fields["pinned"] = True
        if data.get("pinned") is False:
            update_fields["pinned"] = False
        if data.get("acknowledged") is True:
            update_fields["is_acknowledged"] = True

        updated = 0
        if update_fields:
            updated = qs.update(**update_fields)

        return Response({"updated": updated})


class NotificationStatusViewSet(mixins.UpdateModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    """
    Endpoints that operate on ONE per-user status row.

    PATCH /api/notifications/status/{id}/mark/
      { "read": true, "pinned": true, "acknowledged": true }
    """
    queryset = (
        NotificationsUserStatus.objects.select_related(
            "notification", "notification__website", "notification__actor"
        )
    )
    serializer_class = NotificationFeedItemSerializer  # default for retrieve
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Always scope to the current user
        return super().get_queryset().filter(user=self.request.user)

    @action(detail=True, methods=["patch"], url_path="mark")
    def mark(self, request, pk=None):
        instance = self.get_object()
        ser = NotificationStatusMarkSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(instance)
        return Response(NotificationFeedItemSerializer(instance).data)