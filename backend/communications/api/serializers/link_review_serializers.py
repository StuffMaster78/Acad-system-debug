from __future__ import annotations

from typing import Any
from typing import cast

from rest_framework import serializers

from communications.models.moderation import CommunicationModerationFlag
from communications.services.moderation_service import (
    CommunicationModerationService,
)
from communications.models.link_review import CommunicationLinkReview
from communications.services.link_review_service import (
    CommunicationLinkReviewService,
)

class CommunicationModerationFlagSerializer(serializers.ModelSerializer):
    """
    Read serializer for moderation flags.
    """

    class Meta:
        model = CommunicationModerationFlag
        fields = [
            "id",
            "website",
            "thread",
            "message",
            "status",
            "severity",
            "reason",
            "details",
            "created_by",
            "resolved_by",
            "resolved_at",
            "resolution_note",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields


class CommunicationModerationFlagResolveSerializer(serializers.Serializer):
    """
    Resolve a moderation flag.
    """

    resolution_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def save(self, **kwargs: Any) -> CommunicationModerationFlag:
        """
        Resolve flag through service.
        """
        request = self.context["request"]
        flag = self.context["flag"]
        data = cast(dict[str, Any], self.validated_data)

        return CommunicationModerationService.resolve_flag(
            flag=flag,
            resolved_by=request.user,
            resolution_note=str(data.get("resolution_note", "")),
        )
    

class CommunicationLinkReviewSerializer(serializers.ModelSerializer):
    """
    Read serializer for link review records.
    """

    class Meta:
        model = CommunicationLinkReview
        fields = [
            "id",
            "website",
            "thread",
            "message",
            "url",
            "domain",
            "status",
            "submitted_by",
            "reviewed_by",
            "reviewed_at",
            "decision_note",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CommunicationLinkReviewDecisionSerializer(serializers.Serializer):
    """
    Serializer for approving, rejecting, or blocking a link review.
    """

    decision_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def approve(
        self,
        *,
        review: CommunicationLinkReview,
    ) -> CommunicationLinkReview:
        """
        Approve a link review.
        """
        request = self.context["request"]
        data = cast(dict[str, Any], self.validated_data)

        return CommunicationLinkReviewService.approve(
            review=review,
            reviewed_by=request.user,
            decision_note=str(data.get("decision_note", "")),
        )

    def reject(
        self,
        *,
        review: CommunicationLinkReview,
    ) -> CommunicationLinkReview:
        """
        Reject a link review.
        """
        request = self.context["request"]
        data = cast(dict[str, Any], self.validated_data)

        return CommunicationLinkReviewService.reject(
            review=review,
            reviewed_by=request.user,
            decision_note=str(data.get("decision_note", "")),
        )

    def block(
        self,
        *,
        review: CommunicationLinkReview,
    ) -> CommunicationLinkReview:
        """
        Block a link review.
        """
        request = self.context["request"]
        data = cast(dict[str, Any], self.validated_data)

        return CommunicationLinkReviewService.block(
            review=review,
            reviewed_by=request.user,
            decision_note=str(data.get("decision_note", "")),
        )
