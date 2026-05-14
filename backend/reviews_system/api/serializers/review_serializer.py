from decimal import Decimal

from rest_framework import serializers

from reviews_system.models.review import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and reading reviews.
    """

    class Meta:
        model = Review
        fields = (
            "id",
            "reviewer_id",
            "target_type",
            "target_id",
            "writer_id",
            "rating",
            "title",
            "comment",
            "rating_payload",
            "moderation_state",
            "visibility",
            "is_verified",
            "created_at",
        )
        read_only_fields = (
            "id",
            "moderation_state",
            "visibility",
            "created_at",
        )

    def validate_rating(self, value: Decimal) -> Decimal:
        """
        Basic API-level guard (domain validation happens elsewhere).
        """

        if value < Decimal("0"):
            raise serializers.ValidationError(
                "Rating cannot be below 0."
            )

        if value > Decimal("5"):
            raise serializers.ValidationError(
                "Rating cannot exceed 5."
            )

        return value