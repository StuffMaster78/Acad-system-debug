from __future__ import annotations

from rest_framework import serializers

from files_management.models import FileAttachment, ManagedFile


class ManagedFileSerializer(serializers.ModelSerializer):
    """
    Read-only representation of uploaded files.
    """

    class Meta:
        model = ManagedFile
        fields = [
            "id",
            "original_name",
            "file_size",
            "mime_type",
            "file_kind",
            "lifecycle_status",
            "scan_status",
            "created_at",
        ]
        read_only_fields = fields


class FileAttachmentSerializer(serializers.ModelSerializer):
    """
    Representation of file attachments.
    """

    managed_file = ManagedFileSerializer(read_only=True)

    class Meta:
        model = FileAttachment
        fields = [
            "id",
            "purpose",
            "visibility",
            "is_primary",
            "managed_file",
            "attached_at",
        ]
        read_only_fields = fields


class FileUploadSerializer(serializers.Serializer):
    """
    Upload input serializer.
    """

    file = serializers.FileField()
    purpose = serializers.CharField(max_length=64)
    is_public = serializers.BooleanField(default=False)


class FileAttachSerializer(serializers.Serializer):
    """
    Attach file to object.
    """

    file_id = serializers.IntegerField()
    object_id = serializers.IntegerField()
    content_type = serializers.CharField()
    purpose = serializers.CharField(max_length=64)
    visibility = serializers.CharField(max_length=64)


class FileDeletionRequestSerializer(serializers.Serializer):
    """
    Request deletion input.
    """

    attachment_id = serializers.IntegerField()
    reason = serializers.CharField()
    scope = serializers.CharField(default="detach_only")