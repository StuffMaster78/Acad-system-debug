from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanManageCommunicationParticipants
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationParticipantSerializer
from communications.models.participant import CommunicationParticipant
from communications.selectors.participant_selectors import (
    CommunicationParticipantSelector,
)
from communications.services.participant_service import (
    CommunicationParticipantService,
)
from communications.api.pagination import CommunicationDefaultPagePagination


class CommunicationParticipantViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for communication participants.
    """

    serializer_class = CommunicationParticipantSerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanManageCommunicationParticipants,
    ]
    pagination_class = CommunicationDefaultPagePagination

    def get_queryset(self):  # type: ignore[override]
        """
        Return participant records visible to staff operators.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationParticipantSelector.for_website(website=website)
            .select_related("website", "thread", "user", "added_by")
            .order_by("-joined_at", "-id")
        )

    def destroy(self, request, *args: Any, **kwargs: Any):
        """
        Remove participant access instead of deleting the row.
        """
        participant = self.get_object()

        CommunicationParticipantService.remove_participant(
            thread=participant.thread,
            user=participant.user,
            removed_by=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)