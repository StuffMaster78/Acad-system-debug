from __future__ import annotations

from rest_framework import serializers

from communications.api.serializers.message_serializers import (
    CommunicationMessageSerializer,
)
from communications.models import CommunicationMessage
from tickets.services import TicketMessageService


class TicketMessageSerializer(CommunicationMessageSerializer):
    class Meta(CommunicationMessageSerializer.Meta):
        pass


class TicketMessageCreateSerializer(serializers.Serializer):
    body = serializers.CharField(
        required=False,
        allow_blank=False,
    )
    message = serializers.CharField(
        required=False,
        allow_blank=False,
        write_only=True,
    )
    content = serializers.CharField(
        required=False,
        allow_blank=False,
        write_only=True,
    )
    parent = serializers.PrimaryKeyRelatedField(
        queryset=CommunicationMessage.objects.all(),
        required=False,
        allow_null=True,
    )
    is_internal = serializers.BooleanField(default=False)
    metadata = serializers.DictField(required=False)

    def validate(self, attrs):
        if "body" not in attrs and "message" in attrs:
            attrs["body"] = attrs["message"]
        if "body" not in attrs and "content" in attrs:
            attrs["body"] = attrs["content"]
        if "body" not in attrs:
            raise serializers.ValidationError(
                {"body": "This field is required."},
            )
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        ticket = self.context["ticket"]
        return TicketMessageService.add_message(
            ticket=ticket,
            sender=request.user,
            body=validated_data["body"],
            is_internal=validated_data.get("is_internal", False),
            parent=validated_data.get("parent"),
            metadata=validated_data.get("metadata"),
            ip_address=self._get_ip_address(request=request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

    def _get_ip_address(self, *, request) -> str | None:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
