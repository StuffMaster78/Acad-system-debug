from rest_framework import generics, status
from rest_framework.response import Response

from reviews_system.api.serializers.review_serializer import (
    ReviewSerializer,
)
from reviews_system.services.review_creation_service import (
    ReviewCreationService,
)


class ReviewCreateView(generics.CreateAPIView):
    """
    Create a new review.
    """

    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = ReviewCreationService.create_review(
            **serializer.validated_data,
        )

        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )