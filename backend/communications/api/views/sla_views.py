from __future__ import annotations

from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanViewCommunicationSLA
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationThreadSLASerializer
from communications.models.sla import CommunicationThreadSLA
from communications.selectors.sla_selectors import CommunicationThreadSLASelector
from communications.api.pagination import CommunicationDefaultPagePagination


class CommunicationThreadSLAViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for communication SLA records.
    """

    serializer_class = CommunicationThreadSLASerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanViewCommunicationSLA,
    ]
    pagination_class = CommunicationDefaultPagePagination

    def get_queryset(self): # type: ignore[override]
        """
        Return SLA records for staff operators.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationThreadSLASelector.for_website(website=website)
            .select_related("website", "thread")
            .order_by("-is_breached", "next_response_due_at", "id")
        )