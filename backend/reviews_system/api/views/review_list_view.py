from rest_framework import generics

from typing import cast
from django.db.models import QuerySet

from reviews_system.api.serializers.review_serializer import (
    ReviewSerializer,
)
from reviews_system.selectors.review_selectors import (
    ReviewSelectors,
)
from reviews_system.models.review import Review

class ReviewListView(generics.ListAPIView):
    """
    List public reviews only.
    """

    serializer_class = ReviewSerializer

    def get_queryset( # type: ignore[reportIncompatibleMethodOverride]
            self
        ) -> QuerySet[Review]:
        return cast(
            QuerySet[Review],
            ReviewSelectors.public_reviews(),
        )