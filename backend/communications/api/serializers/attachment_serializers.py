from __future__ import annotations

from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from communications.models.attachment import CommunicationAttachment
from communications.services.attachment_service import (
    CommunicationAttachmentService,
)
class CommunicationAttachmentSerializer(serializers.ModelSerializer):
    """
    Read serializer for communication attachments.
    """

    uploaded_by_display = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationAttachment
        fields = [
            "id",
            "website",
            "thread",
            "message",
            "file",
            "uploaded_by",
            "uploaded_by_display",
            "is_visible",
            "requires_moderation",
            "created_at",
        ]
        read_only_fields = fields

    def get_uploaded_by_display(
        self,
        obj: CommunicationAttachment,
    ) -> str:
        """
        Return uploader display label.
        """
        if obj.uploaded_by is None:
            return ""

        if hasattr(obj.uploaded_by, "get_full_name"):
            full_name = obj.uploaded_by.get_full_name()
            if full_name:
                return full_name

        return getattr(obj.uploaded_by, "email", str(obj.uploaded_by))

class CommunicationAttachmentCreateSerializer(serializers.Serializer):
    """
    Attach an existing managed file to a message.
    """

    file_id = serializers.IntegerField()
    requires_moderation = serializers.BooleanField(
        required=False,
        allow_null=True,
    )

    def create(self, validated_data: dict[str, Any]) -> CommunicationAttachment:
        """
        Attach file through service.
        """
        request = self.context["request"]
        message = self.context["message"]

        # Replace this import/model with your actual files_management model.
        from files_management.models import ManagedFile

        try:
            file = ManagedFile.objects.get(
                pk=validated_data["file_id"],
                website=message.website,
            )
        except ObjectDoesNotExist as exc:
            raise serializers.ValidationError(
                {"file_id": "Managed file was not found for this website."},
            ) from exc

        return CommunicationAttachmentService.attach_file(
            message=message,
            file=file,
            uploaded_by=request.user,
            requires_moderation=validated_data.get("requires_moderation"),
        )
