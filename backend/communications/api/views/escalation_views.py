from __future__ import annotations

from typing import Any

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanEscalateCommunicationThread
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationEscalationResolveSerializer
from communications.api.serializers import CommunicationEscalationSerializer
from communications.models.escalation import CommunicationEscalation
from communications.selectors.escalation_selectors import (
    CommunicationEscalationSelector,
)
from communications.api.pagination import CommunicationDefaultPagePagination


class CommunicationEscalationViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for communication escalations.
    """

    serializer_class = CommunicationEscalationSerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanEscalateCommunicationThread,
    ]
    pagination_class = CommunicationDefaultPagePagination
    
    def get_queryset(self):  # type: ignore[override]
        """
        Return escalations visible to staff operators.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationEscalationSelector.for_website(website=website)
            .select_related(
                "website",
                "thread",
                "escalated_by",
                "resolved_by",
            )
            .order_by("-escalated_at", "-id")
        )

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """
        Resolve an escalation.
        """
        escalation = self.get_object()

        serializer = CommunicationEscalationResolveSerializer(
            data=request.data,
            context={
                "request": request,
                "escalation": escalation,
            },
        )
        serializer.is_valid(raise_exception=True)
        resolved_escalation = serializer.save()

        output = CommunicationEscalationSerializer(resolved_escalation)
        return Response(output.data)