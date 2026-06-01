from __future__ import annotations

from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanManageThreadTags
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationThreadTagCreateSerializer
from communications.api.serializers import CommunicationThreadTagSerializer
from communications.api.serializers import (
    CommunicationThreadTagAssignmentSerializer,
)
from communications.models.tag import CommunicationThreadTag
from communications.models.tag import CommunicationThreadTagAssignment
from communications.selectors.tag_selectors import (
    CommunicationThreadTagAssignmentSelector,
)
from communications.selectors.tag_selectors import CommunicationThreadTagSelector


class CommunicationThreadTagViewSet(ModelViewSet):
    """
    API endpoints for communication thread tags.
    """

    permission_classes = [
        IsAuthenticatedForCommunications,
        CanManageThreadTags,
    ]

    def get_queryset(self): # type: ignore[override]
        """
        Return tags for the request website.
        """
        website = getattr(self.request, "website", None)

        return CommunicationThreadTagSelector.for_website(
            website=website,
        ).order_by("name", "id")

    def get_serializer_class(self): # type: ignore[override]
        """
        Return serializer class.
        """
        if self.action == "create":
            return CommunicationThreadTagCreateSerializer

        return CommunicationThreadTagSerializer


class CommunicationThreadTagAssignmentViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for tag assignments.
    """

    serializer_class = CommunicationThreadTagAssignmentSerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanManageThreadTags,
    ]

    def get_queryset(self): # type: ignore[override]
        """
        Return tag assignments for a website.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationThreadTagAssignment.objects
            .filter(website=website)
            .select_related("website", "thread", "tag")
            .order_by("-created_at", "-id")
        )