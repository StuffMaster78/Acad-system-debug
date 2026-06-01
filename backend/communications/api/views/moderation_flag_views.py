from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanModerateCommunication
from communications.api.permissions import CanViewModerationQueue
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import (
    CommunicationModerationFlagResolveSerializer,
)
from communications.api.serializers import CommunicationModerationFlagSerializer
from communications.models.moderation import CommunicationModerationFlag
from communications.selectors.moderation_flag_selectors import (
    CommunicationModerationFlagSelector,
)
from communications.api.throttles import (
    CommunicationModerationActionThrottle,
)
from communications.api.pagination import CommunicationDefaultPagePagination


class CommunicationModerationFlagViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for communication moderation flags.
    """

    serializer_class = CommunicationModerationFlagSerializer
    pagination_class = CommunicationDefaultPagePagination

    def get_permissions(self): # type: ignore[override]
        """
        Return permissions by action.
        """
        if self.action == "resolve":
            permission_classes = [
                IsAuthenticatedForCommunications,
                CanModerateCommunication,
            ]
        else:
            permission_classes = [
                IsAuthenticatedForCommunications,
                CanViewModerationQueue,
            ]

        return [permission() for permission in permission_classes]

    def get_queryset(self): # type: ignore[override]
        """
        Return moderation flags visible to staff operators.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationModerationFlagSelector.for_website(website=website)
            .select_related(
                "website",
                "thread",
                "message",
                "created_by",
                "resolved_by",
            )
            .order_by("-created_at", "-id")
        )

    @action(
        detail=True,
        methods=["post"],
        throttle_classes=[CommunicationModerationActionThrottle],
    )
    def resolve(self, request, pk=None):
        """
        Resolve a moderation flag.
        """
        flag = self.get_object()

        serializer = CommunicationModerationFlagResolveSerializer(
            data=request.data,
            context={
                "request": request,
                "flag": flag,
            },
        )
        serializer.is_valid(raise_exception=True)
        resolved_flag = serializer.save()

        output = CommunicationModerationFlagSerializer(resolved_flag)
        return Response(output.data)