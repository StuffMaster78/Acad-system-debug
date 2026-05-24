from __future__ import annotations

from typing import Any
from typing import cast

from rest_framework import serializers

from communications.models.moderation import CommunicationModerationFlag
from communications.services.moderation_service import (
    CommunicationModerationService,
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
