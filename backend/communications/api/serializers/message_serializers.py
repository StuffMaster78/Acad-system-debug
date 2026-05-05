from __future__ import annotations

from typing import Any

from rest_framework import serializers

from communications.models.message import CommunicationMessage
from communications.services.message_edit_service import (
    CommunicationMessageEditService,
)
from communications.services.message_service import CommunicationMessageService


class CommunicationMessageSerializer(serializers.ModelSerializer):
    """
    Read serializer for communication messages.
    """

    sender_display = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationMessage
        fields = [
            "id",
            "website",
            "thread",
            "sender",
            "sender_display",
            "message_type",
            "status",
            "body",
            "parent",
            "is_internal",
            "is_system_generated",
            "is_edited",
            "edited_at",
            "hidden_at",
            "withdrawn_at",
            "deleted_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_sender_display(self, obj: CommunicationMessage) -> str:
        """
        Return safe sender display.
        """
        if obj.sender is None:
            return "System"

        if hasattr(obj.sender, "get_full_name"):
            full_name = obj.sender.get_full_name()
            if full_name:
                return full_name

        return getattr(obj.sender, "email", str(obj.sender))


class CommunicationMessageCreateSerializer(serializers.Serializer):
    """
    Create serializer for user messages.
    """

    body = serializers.CharField(allow_blank=False)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=CommunicationMessage.objects.all(),
        required=False,
        allow_null=True,
    )
    is_internal = serializers.BooleanField(default=False)
    metadata = serializers.DictField(required=False)

    def create(self, validated_data: dict[str, Any]) -> CommunicationMessage:
        """
        Create message through the message service.
        """
        request = self.context["request"]
        thread = self.context["thread"]

        return CommunicationMessageService.create_message(
            thread=thread,
            sender=request.user,
            body=validated_data["body"],
            website=getattr(request, "website", thread.website),
            parent=validated_data.get("parent"),
            is_internal=validated_data.get("is_internal", False),
            metadata=validated_data.get("metadata"),
            ip_address=self._get_ip_address(request=request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

    def _get_ip_address(self, *, request) -> str | None:
        """
        Extract request IP address.
        """
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR")


class CommunicationMessageEditSerializer(serializers.Serializer):
    """
    Edit a message body.
    """

    body = serializers.CharField(allow_blank=False)

    def update(
        self,
        instance: CommunicationMessage,
        validated_data: dict[str, Any],
    ) -> CommunicationMessage:
        """
        Edit message through the edit service.
        """
        request = self.context["request"]

        return CommunicationMessageEditService.edit_message(
            message=instance,
            new_body=validated_data["body"],
            edited_by=request.user,
        )


class CommunicationMessageActionSerializer(serializers.Serializer):
    """
    Serializer for hide or withdraw actions.
    """

    reason = serializers.CharField(required=False, allow_blank=True)

class CommunicationMessageSearchSerializer(serializers.Serializer):
    """
    Validate message search query.
    """

    query = serializers.CharField(
        max_length=255,
        allow_blank=False,
    )