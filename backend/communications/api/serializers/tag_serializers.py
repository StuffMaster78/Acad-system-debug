from __future__ import annotations

from typing import Any

from rest_framework import serializers

from communications.models.tag import CommunicationThreadTag
from communications.models.tag import CommunicationThreadTagAssignment
from communications.services.tag_service import CommunicationThreadTagService


class CommunicationThreadTagSerializer(serializers.ModelSerializer):
    """
    Read serializer for communication thread tags.
    """

    class Meta:
        model = CommunicationThreadTag
        fields = [
            "id",
            "website",
            "name",
            "color",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CommunicationThreadTagCreateSerializer(serializers.Serializer):
    """
    Create a thread tag.
    """

    name = serializers.CharField(max_length=80)
    color = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def create(self, validated_data: dict[str, Any]) -> CommunicationThreadTag:
        """
        Create tag through service.
        """
        request = self.context["request"]
        website = getattr(request, "website", None)

        return CommunicationThreadTagService.create_tag(
            website=website,
            name=validated_data["name"],
            color=validated_data.get("color", ""),
            description=validated_data.get("description", ""),
        )


class CommunicationThreadTagAssignmentSerializer(serializers.ModelSerializer):
    """
    Read serializer for tag assignments.
    """

    tag_detail = CommunicationThreadTagSerializer(
        source="tag",
        read_only=True,
    )

    class Meta:
        model = CommunicationThreadTagAssignment
        fields = [
            "id",
            "website",
            "thread",
            "tag",
            "tag_detail",
            "created_at",
        ]
        read_only_fields = fields


class CommunicationThreadTagAssignSerializer(serializers.Serializer):
    """
    Assign a tag to a thread.
    """

    tag = serializers.PrimaryKeyRelatedField(
        queryset=CommunicationThreadTag.objects.all(),
    )

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> CommunicationThreadTagAssignment:
        """
        Assign tag through service.
        """
        request = self.context["request"]
        thread = self.context["thread"]

        return CommunicationThreadTagService.assign_tag(
            thread=thread,
            tag=validated_data["tag"],
            actor=request.user,
        )