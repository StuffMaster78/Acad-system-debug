from __future__ import annotations

from rest_framework.viewsets import ModelViewSet

from communications.api.permissions import CanManageSavedReplies
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationSavedReplyCreateSerializer
from communications.api.serializers import CommunicationSavedReplySerializer
from communications.models.saved_reply import CommunicationSavedReply
from communications.selectors.saved_reply_selectors import (
    CommunicationSavedReplySelector,
)


class CommunicationSavedReplyViewSet(ModelViewSet):
    """
    API endpoints for saved replies.
    """

    permission_classes = [
        IsAuthenticatedForCommunications,
        CanManageSavedReplies,
    ]

    def get_queryset(self): # type: ignore[override]
        """
        Return saved replies for the current website.
        """
        website = getattr(self.request, "website", None)

        return CommunicationSavedReplySelector.for_website(
            website=website,
        ).order_by("title", "id")

    def get_serializer_class(self): # type: ignore[override]
        """
        Return serializer class.
        """
        if self.action == "create":
            return CommunicationSavedReplyCreateSerializer

        return CommunicationSavedReplySerializer