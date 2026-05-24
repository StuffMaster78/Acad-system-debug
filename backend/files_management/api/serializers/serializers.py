from __future__ import annotations

from rest_framework import serializers

from files_management.models.file_attachment import FileAttachment
from files_management.models.managed_file import ManagedFile
from files_management.models.file_quota import FileQuota



class ManagedFileSerializer(serializers.ModelSerializer):
    """
    Read-only representation of uploaded files.
    """
    public_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ManagedFile
        fields = [
            "uuid",
            "original_filename",
            "file_size_bytes",
            "mime_type", "file_extension", "file_kind",
            "width_px", "height_px", "page_count",
            "scan_status", "lifecycle_status",
            "is_public", "derivative_type",
            "public_url", "download_url",
            "created_at",
        ]
        read_only_fields = fields


    def get_download_url(self, obj) -> str | None:
        public_url = self.get_public_url(obj)
        if public_url:
            return public_url
        return None

    def get_public_url(self, obj) -> str | None:
        return obj.public_url



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
    bucket_id = serializers.IntegerField(required=False)
    file_kind = serializers.CharField(default="other")
    is_public = serializers.BooleanField(default=False, required=False)


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


class FileQuotaSerializer(serializers.ModelSerializer):
    usage_percent = serializers.FloatField(read_only=True)
    remaining_bytes = serializers.IntegerField(read_only=True)

    class Meta:
        model = FileQuota
        fields = [
            "max_total_size_bytes", "max_file_size_bytes", "max_files_count",
            "current_size_bytes", "current_files_count",
            "usage_percent", "remaining_bytes",
        ]
