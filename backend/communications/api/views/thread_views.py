from __future__ import annotations

from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from communications.api.permissions import CanManageCommunicationParticipants
from communications.api.permissions import CanViewCommunicationThread
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationMessageCreateSerializer
from communications.api.serializers import CommunicationMessageSerializer
from communications.api.serializers import CommunicationParticipantCreateSerializer
from communications.api.serializers import CommunicationParticipantSerializer
from communications.api.serializers import CommunicationThreadCreateSerializer
from communications.api.serializers import CommunicationThreadSerializer
from communications.models.thread import CommunicationThread
from communications.selectors.message_selectors import (
    CommunicationMessageSelector,
)
from communications.selectors.participant_selectors import (
    CommunicationParticipantSelector,
)
from communications.selectors.thread_selectors import CommunicationThreadSelector
from communications.services.thread_guard_service import (
    CommunicationThreadGuardService,
)
from communications.api.serializers import CommunicationReadReceiptSerializer
from communications.services.read_receipt_service import (
    CommunicationReadReceiptService,
)
from communications.api.throttles import CommunicationMessageSendThrottle
from communications.api.throttles import CommunicationReadReceiptThrottle
from communications.api.pagination import CommunicationMessageCursorPagination
from communications.services.thread_service import (
    CommunicationThreadService,
)

class CommunicationThreadViewSet(ModelViewSet):
    """
    API endpoints for communication threads.
    """

    permission_classes = [
        IsAuthenticatedForCommunications,
        CanViewCommunicationThread,
    ]

    def get_queryset( # type: ignore[override]
            self,
        ):
        """
        Return threads visible to the request user.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationThreadSelector.visible_to_user(
                website=website,
                user=self.request.user,
            )
            .select_related("website", "target_content_type", "created_by")
            .order_by("-last_message_at", "-created_at", "-id")
        )

    def get_serializer_class( # type: ignore[override]
            self
        ):
        """
        Return serializer class for the current action.
        """
        if self.action == "create":
            return CommunicationThreadCreateSerializer

        return CommunicationThreadSerializer

    def perform_create(self, serializer):
        """
        Create a thread via service.
        """
        validated = serializer.validated_data

        thread = CommunicationThreadService.create_thread(
            target=validated["target"],
            thread_kind=validated["kind"],
            created_by=self.request.user,
            website=getattr(self.request, "website", None),
        )

        serializer.instance = thread

    def retrieve(self, request, *args: Any, **kwargs: Any):
        """
        Retrieve one visible thread.
        """
        instance = self.get_object()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get", "post"],
        url_path="messages",
        throttle_classes=[CommunicationMessageSendThrottle],
    )
    def messages(self, request, pk=None):
        """
        GET  — list paginated messages for a thread.
        POST — send a new message to the thread.
        """
        thread = self.get_object()

        if request.method == "GET":
            CommunicationThreadGuardService.enforce_can_view_thread(
                user=request.user,
                website=getattr(request, "website", thread.website),
                thread=thread,
            )
            queryset = CommunicationMessageSelector.visible_for_thread(
                website=thread.website,
                user=request.user,
                thread=thread,
            )
            paginator = CommunicationMessageCursorPagination()
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = CommunicationMessageSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            return Response(CommunicationMessageSerializer(queryset, many=True).data)

        # POST
        CommunicationThreadGuardService.enforce_can_send_message(
            user=request.user,
            website=getattr(request, "website", thread.website),
            thread=thread,
        )
        serializer = CommunicationMessageCreateSerializer(
            data=request.data,
            context={"request": request, "thread": thread},
        )
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(CommunicationMessageSerializer(message).data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["get", "post"],
        permission_classes=[
            IsAuthenticatedForCommunications,
            CanManageCommunicationParticipants,
        ],
    )
    def participants(self, request, pk=None):
        """
        List or add thread participants.
        """
        thread = self.get_object()

        if request.method == "GET":
            queryset = CommunicationParticipantSelector.active_for_thread(
                website=thread.website,
                thread=thread,
            )
            serializer = CommunicationParticipantSerializer(
                queryset,
                many=True,
            )
            return Response(serializer.data)

        serializer = CommunicationParticipantCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "thread": thread,
            },
        )
        serializer.is_valid(raise_exception=True)
        participant = serializer.save()

        output = CommunicationParticipantSerializer(participant)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        url_path="mark-read",
        throttle_classes=[CommunicationReadReceiptThrottle],
    )
    def mark_read(self, request, pk=None):
        """
        Mark all messages in this thread as read.
        """
        thread = self.get_object()

        receipts = CommunicationReadReceiptService.mark_thread_read(
            thread=thread,
            user=request.user,
            website=getattr(request, "website", thread.website),
        )

        serializer = CommunicationReadReceiptSerializer(receipts, many=True)
        return Response(serializer.data)