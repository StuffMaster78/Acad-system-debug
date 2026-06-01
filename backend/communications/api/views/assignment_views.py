from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanAssignCommunicationThread
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import (
    CommunicationThreadAssignmentSerializer,
)
from communications.models.assignment import CommunicationThreadAssignment
from communications.selectors.assignment_selectors import (
    CommunicationThreadAssignmentSelector,
)
from communications.services.assignment_service import (
    CommunicationThreadAssignmentService,
)
from communications.api.pagination import CommunicationDefaultPagePagination


class CommunicationThreadAssignmentViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for communication thread assignments.
    """

    serializer_class = CommunicationThreadAssignmentSerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanAssignCommunicationThread,
    ]
    pagination_class = CommunicationDefaultPagePagination

    def get_queryset(self): # type: ignore[override]
        """
        Return thread assignments.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationThreadAssignmentSelector.for_website(website=website)
            .select_related(
                "website",
                "thread",
                "assigned_to",
                "assigned_by",
            )
            .order_by("-assigned_at", "-id")
        )

    def destroy(self, request, *args: Any, **kwargs: Any):
        """
        Deactivate assignment instead of deleting it.
        """
        assignment = self.get_object()

        CommunicationThreadAssignmentService.unassign(
            thread=assignment.thread,
            assigned_to=assignment.assigned_to,
            actor=request.user,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)