from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from communications.models.participant import CommunicationParticipant
from communications.services.participant_service import (
    CommunicationParticipantService,
)


class CommunicationParticipantSerializer(serializers.ModelSerializer):
    """
    Read serializer for thread participants.
    """

    user_display = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationParticipant
        fields = [
            "id",
            "website",
            "thread",
            "user",
            "user_display",
            "role",
            "can_view",
            "can_send",
            "can_upload",
            "is_observer",
            "added_by",
            "joined_at",
            "removed_at",
            "metadata",
        ]
        read_only_fields = fields

    def get_user_display(self, obj: CommunicationParticipant) -> str:
        """
        Return participant display label.
        """
        if hasattr(obj.user, "get_full_name"):
            full_name = obj.user.get_full_name()
            if full_name:
                return full_name

        return getattr(obj.user, "email", str(obj.user))


class CommunicationParticipantCreateSerializer(serializers.Serializer):
    """
    Add participant to a thread.
    """

    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
    )
    role = serializers.CharField(max_length=30)
    can_view = serializers.BooleanField(default=True)
    can_send = serializers.BooleanField(default=True)
    can_upload = serializers.BooleanField(default=True)
    is_observer = serializers.BooleanField(default=False)

    def create(self, validated_data: dict[str, Any]) -> CommunicationParticipant:
        """
        Add participant through service.
        """
        request = self.context["request"]
        thread = self.context["thread"]

        return CommunicationParticipantService.add_participant(
            thread=thread,
            user=validated_data["user"],
            role=validated_data["role"],
            added_by=request.user,
            can_view=validated_data["can_view"],
            can_send=validated_data["can_send"],
            can_upload=validated_data["can_upload"],
            is_observer=validated_data["is_observer"],
        )