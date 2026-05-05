from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanViewCommunicationObject
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationReadReceiptSerializer
from communications.api.serializers import CommunicationUnreadCountSerializer
from communications.models.receipt import CommunicationReadReceipt
from communications.selectors.read_receipt_selectors import (
    CommunicationReadReceiptSelector,
)
from communications.services.read_receipt_service import (
    CommunicationReadReceiptService,
)


class CommunicationReadReceiptViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for read receipts and unread counts.
    """

    serializer_class = CommunicationReadReceiptSerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanViewCommunicationObject,
    ]

    def get_queryset(self):  # type: ignore[override]
        """
        Return receipts visible to user.
        """
        website = getattr(self.request, "website", None)

        if website is None:
            return CommunicationReadReceipt.objects.none()

        return (
            CommunicationReadReceipt.objects
            .filter(website=website, user=self.request.user)
            .select_related("website", "thread", "message", "user")
            .order_by("-read_at", "-id")
        )

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """
        Return unread count for current user.
        """
        website = getattr(request, "website", None)

        unread_count = CommunicationReadReceiptSelector.unread_count_for_user(
            website=website,
            user=request.user,
        )

        serializer = CommunicationUnreadCountSerializer(
            {"unread_count": unread_count},
        )
        return Response(serializer.data)