from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanReviewCommunicationLinks
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationLinkReviewDecisionSerializer
from communications.api.serializers import CommunicationLinkReviewSerializer
from communications.models.link_review import CommunicationLinkReview
from communications.selectors.link_review_selectors import (
    CommunicationLinkReviewSelector,
)
from communications.api.throttles import CommunicationModerationActionThrottle
from communications.api.pagination import CommunicationDefaultPagePagination

class CommunicationLinkReviewViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for communication link reviews.
    """

    serializer_class = CommunicationLinkReviewSerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanReviewCommunicationLinks,
    ]
    pagination_class = CommunicationDefaultPagePagination

    def get_queryset(self): # type: ignore[override]
        """
        Return link reviews.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationLinkReviewSelector.for_website(website=website)
            .select_related(
                "website",
                "thread",
                "message",
                "submitted_by",
                "reviewed_by",
            )
            .order_by("-created_at", "-id")
        )

    @action(
        detail=True,
        methods=["post"],
        throttle_classes=[CommunicationModerationActionThrottle],
    )
    def approve(self, request, pk=None):
        """
        Approve a link review.
        """
        review = self.get_object()

        serializer = CommunicationLinkReviewDecisionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_review = serializer.approve(review=review)

        output = CommunicationLinkReviewSerializer(updated_review)
        return Response(output.data)

    @action(
        detail=True,
        methods=["post"],
        throttle_classes=[CommunicationModerationActionThrottle],
    )
    def reject(self, request, pk=None):
        """
        Reject a link review.
        """
        review = self.get_object()

        serializer = CommunicationLinkReviewDecisionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_review = serializer.reject(review=review)

        output = CommunicationLinkReviewSerializer(updated_review)
        return Response(output.data)

    @action(
        detail=True,
        methods=["post"],
        throttle_classes=[CommunicationModerationActionThrottle],
    )
    def block(self, request, pk=None):
        """
        Block a link review.
        """
        review = self.get_object()

        serializer = CommunicationLinkReviewDecisionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated_review = serializer.block(review=review)

        output = CommunicationLinkReviewSerializer(updated_review)
        return Response(output.data)