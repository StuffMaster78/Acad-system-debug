from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanHideOrWithdrawMessage
from communications.api.permissions import CanViewCommunicationObject
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationAttachmentSerializer
from communications.models.attachment import CommunicationAttachment
from communications.selectors.attachment_selectors import (
    CommunicationAttachmentSelector,
)
from communications.services.attachment_service import (
    CommunicationAttachmentService,
)


class CommunicationAttachmentViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for communication attachments.
    """

    serializer_class = CommunicationAttachmentSerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanViewCommunicationObject,
    ]

    def get_queryset(self):  # type: ignore[override]
        """
        Return attachments visible to the request user.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationAttachmentSelector.visible_to_user(
                website=website,
                user=self.request.user,
            )
            .select_related(
                "website",
                "thread",
                "message",
                "file",
                "uploaded_by",
            )
            .order_by("-created_at", "-id")
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticatedForCommunications,
            CanHideOrWithdrawMessage,
        ],
    )
    def hide(self, request, pk=None):
        """
        Hide an attachment.
        """
        attachment = self.get_object()

        hidden_attachment = CommunicationAttachmentService.hide_attachment(
            attachment=attachment,
            actor=request.user,
            reason=str(request.data.get("reason", "")),
        )

        serializer = CommunicationAttachmentSerializer(hidden_attachment)
        return Response(serializer.data, status=status.HTTP_200_OK)