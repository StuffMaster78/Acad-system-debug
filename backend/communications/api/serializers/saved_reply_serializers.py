from __future__ import annotations

from typing import Any

from rest_framework import serializers

from communications.models.saved_reply import CommunicationSavedReply
from communications.services.saved_reply_service import (
    CommunicationSavedReplyService,
)


class CommunicationSavedReplySerializer(serializers.ModelSerializer):
    """
    Read serializer for saved replies.
    """

    class Meta:
        model = CommunicationSavedReply
        fields = [
            "id",
            "website",
            "title",
            "body",
            "category",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CommunicationSavedReplyCreateSerializer(serializers.Serializer):
    """
    Create saved replies.
    """

    title = serializers.CharField(max_length=120)
    body = serializers.CharField()
    category = serializers.CharField(
        max_length=80,
        required=False,
        allow_blank=True,
    )

    def create(self, validated_data: dict[str, Any]) -> CommunicationSavedReply:
        """
        Create saved reply through service.
        """
        request = self.context["request"]
        website = getattr(request, "website", None)

        return CommunicationSavedReplyService.create(
            website=website,
            title=validated_data["title"],
            body=validated_data["body"],
            category=validated_data.get("category", ""),
            created_by=request.user,
        )