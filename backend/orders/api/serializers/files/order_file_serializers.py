from __future__ import annotations

from rest_framework import serializers

from files_management.enums import FilePurpose
from files_management.models import FileAttachment
from files_management.api.serializers.response_serializers import (
    FileAttachmentDetailSerializer,
)


class OrderFileUploadSerializer(serializers.Serializer):
    """
    Serializer for order file uploads.
    """

    file = serializers.FileField()


class OrderExternalFileLinkSerializer(serializers.Serializer):
    """
    Serializer for order external file links.
    """

    url = serializers.URLField()
    title = serializers.CharField(required=False, allow_blank=True)
    purpose = serializers.ChoiceField(
        choices=[
            FilePurpose.ORDER_INSTRUCTION,
            FilePurpose.ORDER_REFERENCE,
            FilePurpose.ORDER_DRAFT,
            FilePurpose.ORDER_FINAL,
            FilePurpose.ORDER_REVISION,
            FilePurpose.STYLE_REFERENCE,
            FilePurpose.EXTRA_SERVICE_FILE,
        ]
    )


class OrderFileDeletionRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting order file deletion.
    """

    reason = serializers.CharField()
    scope = serializers.CharField(default="detach_only")


class OrderFileAttachmentSerializer(FileAttachmentDetailSerializer):
    """
    Read serializer for order file attachments.
    """

    class Meta(FileAttachmentDetailSerializer.Meta):
        model = FileAttachment