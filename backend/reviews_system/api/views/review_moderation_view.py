from rest_framework import generics, status
from rest_framework.response import Response

from reviews_system.api.serializers.review_serializer import (
    ReviewSerializer,
)
from reviews_system.selectors.review_selectors import (
    ReviewSelectors,
)
from reviews_system.services.review_moderation_service import (
    ReviewModerationService,
)


class ReviewModerationView(generics.UpdateAPIView):
    """
    Moderate a review (approve, reject, shadow, flag).
    """

    serializer_class = ReviewSerializer
    queryset = ReviewSelectors.all_reviews()

    def update(self, request, *args, **kwargs):
        review = self.get_object()

        serializer = self.get_serializer(
            review,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data.get("action")

        reason = serializer.validated_data.get("reason", "")
        moderator_id = serializer.validated_data.get(
            "moderator_id",
            None,
        )

        if action == "approve":
            ReviewModerationService.approve(
                review=review,
                moderator_id=moderator_id,
                reason=reason,
            )

        elif action == "reject":
            ReviewModerationService.reject(
                review=review,
                moderator_id=moderator_id,
                reason=reason,
            )

        elif action == "shadow":
            ReviewModerationService.shadow(
                review=review,
                moderator_id=moderator_id,
                reason=reason,
            )

        elif action == "flag":
            ReviewModerationService.flag(
                review=review,
                moderator_id=moderator_id,
                reason=reason,
            )

        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_200_OK,
        )