from rest_framework import serializers
from reviews_system.models import WebsiteReview, WriterReview, OrderReview


class WebsiteReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for website-level reviews.

    Attributes:
        reviewer_name (str): Full name of the reviewer (read-only).
    """

    reviewer_name = serializers.CharField(
        source="reviewer.get_full_name", read_only=True
    )

    class Meta:
        model = WebsiteReview
        fields = [
            "id", "website", "reviewer", "reviewer_name", "rating", "comment",
            "origin", "is_approved", "is_shadowed", "is_flagged", "flag_reason",
            "submitted_at"
        ]
        read_only_fields = [
            "reviewer", "origin", "is_approved", "is_shadowed", "is_flagged", 
            "flag_reason"
        ]


class WriterReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for reviews written about writers.

    Attributes:
        reviewer_name (str): Full name of the reviewer (read-only).
        writer_name (str): Full name of the writer being reviewed (read-only).
    """

    reviewer_name = serializers.CharField(
        source="reviewer.get_full_name", read_only=True
    )
    writer_name = serializers.CharField(
        source="writer.get_full_name", read_only=True
    )

    class Meta:
        model = WriterReview
        fields = [
            "id", "website", "writer", "writer_name", "reviewer", "reviewer_name",
            "rating", "comment", "origin", "is_approved", "is_shadowed", 
            "is_flagged", "flag_reason", "submitted_at"
        ]
        read_only_fields = [
            "reviewer", "origin", "is_approved", "is_shadowed", "is_flagged",
            "flag_reason"
        ]


class OrderReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for reviews left on specific orders.

    Attributes:
        reviewer_name (str): Full name of the reviewer (read-only).
        writer_name (str): Full name of the writer who handled the order (read-only).
    """

    reviewer_name = serializers.CharField(
        source="reviewer.get_full_name", read_only=True
    )
    writer_name = serializers.CharField(
        source="writer.get_full_name", read_only=True
    )

    class Meta:
        model = OrderReview
        fields = [
            "id", "website", "order", "writer", "writer_name", "reviewer", 
            "reviewer_name", "rating", "comment", "origin", "is_approved",
            "is_shadowed", "is_flagged", "flag_reason", "submitted_at"
        ]
        read_only_fields = [
            "reviewer", "origin", "is_approved", "is_shadowed", "is_flagged", 
            "flag_reason"
        ]


class ReviewModerationSerializer(serializers.Serializer):
    """
    Serializer for admins to approve, shadow, or flag a review.

    Fields:
        is_approved (bool): Marks review as approved.
        is_shadowed (bool): Prevents review from being visible to frontend users.
        flag_reason (str): Reason for flagging the review for admin attention.
    """

    is_approved = serializers.BooleanField(required=False)
    is_shadowed = serializers.BooleanField(required=False)
    flag_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        """
        Validates that at least one moderation action is provided.

        Returns:
            dict: Cleaned and validated attributes.

        Raises:
            serializers.ValidationError: If no valid fields are present.
        """
        if not any(k in attrs for k in ["is_approved", "is_shadowed", "flag_reason"]):
            raise serializers.ValidationError(
                "Provide at least one moderation field."
            )
        return attrs


class ReviewDisputeSerializer(serializers.Serializer):
    """
    Serializer for a writer to dispute a review left by a client.

    Fields:
        reason (str): Justification or objection to the review.
    """

    reason = serializers.CharField()

    def validate_reason(self, value):
        """
        Ensures that dispute reason is detailed enough.

        Args:
            value (str): Provided reason text.

        Returns:
            str: Validated reason.

        Raises:
            serializers.ValidationError: If reason is too short.
        """
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Please provide a more detailed reason for the dispute."
            )
        return value