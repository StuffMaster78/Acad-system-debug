from __future__ import annotations

from rest_framework import serializers

from files_management.api.serializers.response_serializers import (
    FileAttachmentDetailSerializer,
)
from tickets.services import TicketFileService


class TicketFileSerializer(FileAttachmentDetailSerializer):
    class Meta(FileAttachmentDetailSerializer.Meta):
        pass


class TicketFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    is_internal = serializers.BooleanField(default=False)
    metadata = serializers.DictField(required=False)

    def create(self, validated_data):
        request = self.context["request"]
        ticket = self.context["ticket"]
        return TicketFileService.attach_ticket_file(
            ticket=ticket,
            uploaded_by=request.user,
            uploaded_file=validated_data["file"],
            is_internal=validated_data.get("is_internal", False),
            metadata=validated_data.get("metadata"),
        )
