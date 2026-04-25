from typing import Any, cast

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.draft_permissions import (
    CanReviewDraft,
    CanSubmitDraft,
)
from orders.api.serializers.drafts.draft_serializers import (
    ReviewDraftSerializer,
    SubmitDraftSerializer,
)
from orders.models.orders.order import Order
from orders.models.drafts.draft import OrderDraft
from orders.models.progresssive_delivery.progressive_delivery import OrderMilestone
from orders.services.draft_service import DraftService


class SubmitDraftView(GenericAPIView):
    serializer_class = SubmitDraftSerializer
    permission_classes = [permissions.IsAuthenticated, CanSubmitDraft]

    def post(self, request: Request, order_id: int) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(Any, request.user)

        order = get_object_or_404(
            Order,
            pk=order_id,
            website=user.website,
        )

        self.check_object_permissions(request, order)

        milestone = None
        milestone_id = serializer.validated_data.get("milestone_id")

        if milestone_id:
            milestone = get_object_or_404(
                OrderMilestone,
                pk=milestone_id,
                order=order,
            )

        try:
            draft = DraftService.submit_draft(
                order=order,
                submitted_by=user,
                milestone=milestone,
                note=serializer.validated_data.get("note", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)

        return Response(
            {
                "draft_id": draft.pk,
                "status": draft.status,
            },
            status=status.HTTP_201_CREATED,
        )


class ReviewDraftView(GenericAPIView):
    serializer_class = ReviewDraftSerializer
    permission_classes = [permissions.IsAuthenticated, CanReviewDraft]

    def post(self, request: Request, draft_id: int) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        draft = get_object_or_404(OrderDraft, pk=draft_id)

        try:
            draft = DraftService.review_draft(
                draft=draft,
                reviewed_by=request.user,
                approve=serializer.validated_data["approve"],
            )
        except DjangoValidationError as exc:
            raise ValidationError(exc.messages)

        return Response(
            {
                "draft_id": draft.pk,
                "status": draft.status,
            },
            status=status.HTTP_200_OK,
        )