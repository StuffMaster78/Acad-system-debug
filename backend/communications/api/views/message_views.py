from __future__ import annotations

from typing import Any, cast

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanEditCommunicationMessage
from communications.api.permissions import CanHideOrWithdrawMessage
from communications.api.permissions import CanViewCommunicationObject
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationMessageActionSerializer
from communications.api.serializers import CommunicationMessageEditSerializer
from communications.api.serializers import CommunicationMessageSerializer
from communications.models.message import CommunicationMessage
from communications.selectors.message_selectors import (
    CommunicationMessageSelector,
)
from communications.services.message_service import CommunicationMessageService
from communications.api.serializers import CommunicationReadReceiptSerializer
from communications.services.read_receipt_service import (
    CommunicationReadReceiptService,
)
from communications.api.throttles import (
    CommunicationModerationActionThrottle,
    CommunicationReadReceiptThrottle,
)
from communications.api.pagination import CommunicationMessageCursorPagination
from communications.api.pagination import CommunicationDefaultPagePagination


from communications.api.serializers import (
    CommunicationAttachmentCreateSerializer,
)
from communications.api.serializers import CommunicationAttachmentSerializer
from communications.selectors.attachment_selectors import (
    CommunicationAttachmentSelector,
)
from communications.api.serializers.message_serializers import (
    CommunicationMessageSearchSerializer,
)
from communications.selectors.message_search_selectors import (
    CommunicationMessageSearchSelector,
)

class CommunicationMessageViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for communication messages.
    """

    serializer_class = CommunicationMessageSerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanViewCommunicationObject,
    ]
    pagination_class = CommunicationDefaultPagePagination

    def get_queryset( # type: ignore[override]
            self
        ):
        """
        Return messages visible to the request user.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationMessageSelector.visible_to_user(
                website=website,
                user=self.request.user,
            )
            .select_related("website", "thread", "sender", "parent")
            .order_by("-created_at", "-id")
        )

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[
            IsAuthenticatedForCommunications,
            CanEditCommunicationMessage,
        ],
        throttle_classes=[CommunicationModerationActionThrottle],
    )
    def edit(self, request, pk=None):
        """
        Edit a message body.
        """
        message = self.get_object()

        serializer = CommunicationMessageEditSerializer(
            instance=message,
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_message = serializer.save()

        output = CommunicationMessageSerializer(updated_message)
        return Response(output.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticatedForCommunications,
            CanHideOrWithdrawMessage,
        ],
        throttle_classes=[CommunicationModerationActionThrottle],
    )
    def hide(self, request, pk=None):
        """
        Hide a message.
        """
        message = self.get_object()

        serializer = CommunicationMessageActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        hidden_message = CommunicationMessageService.mark_message_hidden(
            message=message,
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )

        output = CommunicationMessageSerializer(hidden_message)
        return Response(output.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            IsAuthenticatedForCommunications,
            CanHideOrWithdrawMessage,
        ],
        throttle_classes=[CommunicationModerationActionThrottle],
    )
    def withdraw(self, request, pk=None):
        """
        Withdraw a message.
        """
        message = self.get_object()

        serializer = CommunicationMessageActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        withdrawn_message = CommunicationMessageService.withdraw_message(
            message=message,
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )

        output = CommunicationMessageSerializer(withdrawn_message)
        return Response(output.data, status=status.HTTP_200_OK)
    

    @action(
        detail=True,
        methods=["post"],
        throttle_classes=[CommunicationReadReceiptThrottle],
    )
    def read(self, request, pk=None):
        """
        Mark this message as read.
        """
        message = self.get_object()

        receipt = CommunicationReadReceiptService.mark_message_read(
            message=message,
            user=request.user,
            website=getattr(request, "website", message.website),
        )

        serializer = CommunicationReadReceiptSerializer(receipt)
        return Response(serializer.data)
    

    @action(detail=True, methods=["get", "post"])
    def attachments(self, request, pk=None):
        """
        List or attach files to a message.
        """
        message = self.get_object()

        if request.method == "GET":
            queryset = CommunicationAttachmentSelector.visible_for_message(
                website=message.website,
                user=request.user,
                message=message,
            )
            serializer = CommunicationAttachmentSerializer(
                queryset,
                many=True,
            )
            return Response(serializer.data)

        serializer = CommunicationAttachmentCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "message": message,
            },
        )
        serializer.is_valid(raise_exception=True)
        attachment = serializer.save()

        output = CommunicationAttachmentSerializer(attachment)
        return Response(output.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Search visible messages.
        """
        serializer = CommunicationMessageSearchSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        queryset = CommunicationMessageSearchSelector.search_visible_messages(
            website=getattr(request, "website", None),
            user=request.user,
            query=str(data["query"]),
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            output = CommunicationMessageSerializer(page, many=True)
            return self.get_paginated_response(output.data)

        output = CommunicationMessageSerializer(queryset, many=True)
        return Response(output.data)