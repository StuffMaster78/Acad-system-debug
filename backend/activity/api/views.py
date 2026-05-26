from __future__ import annotations

from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from activity.api.serializers import ActivityEventSerializer
from activity.models import ActivityEvent
from activity.permissions import CanViewActivityEvent
from activity.selectors.event_selectors import ActivityEventSelector
from activity.services.feed_state_service import ActivityFeedStateService
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter

from activity.api.filters import ActivityEventFilter

class ActivityFeedViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    API endpoint for the authenticated user's activity feed.
    """

    serializer_class = ActivityEventSerializer
    permission_classes = [CanViewActivityEvent]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = ActivityEventFilter
    search_fields = [
        "title",
        "summary",
        "metadata",
    ]
    ordering_fields = [
        "occurred_at",
        "created_at",
        "severity",
        "verb",
    ]
    ordering = [
        "-occurred_at",
        "-created_at",
    ]

    def get_queryset(self): # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Return activity events visible to the current user.
        """
        request = self.request
        website = getattr(request, "website", None)

        if website is None:
            role = getattr(request.user, "role", "")
            if role in {"admin", "superadmin"} or getattr(request.user, "is_superuser", False):
                return ActivityEventSelector.visible_to_user_global(
                    user=request.user,
                )
            return ActivityEvent.objects.none()

        return ActivityEventSelector.visible_to_user(
            website=website,
            user=request.user,
        )

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        """
        Mark an activity event as read for the current user.
        """
        event = self.get_object()

        ActivityFeedStateService.mark_read(
            event=event,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="mark-unread")
    def mark_unread(self, request, pk=None):
        """
        Mark an activity event as unread for the current user.
        """
        event = self.get_object()

        ActivityFeedStateService.mark_unread(
            event=event,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="dismiss")
    def dismiss(self, request, pk=None):
        """
        Dismiss an activity event for the current user.
        """
        event = self.get_object()

        ActivityFeedStateService.dismiss(
            event=event,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """
        Restore a dismissed activity event for the current user.
        """
        event = self.get_object()

        ActivityFeedStateService.restore(
            event=event,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="pin")
    def pin(self, request, pk=None):
        """
        Pin an activity event for the current user.
        """
        event = self.get_object()

        ActivityFeedStateService.pin(
            event=event,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="unpin")
    def unpin(self, request, pk=None):
        """
        Unpin an activity event for the current user.
        """
        event = self.get_object()

        ActivityFeedStateService.unpin(
            event=event,
            user=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
