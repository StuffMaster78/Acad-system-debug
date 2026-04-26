from rest_framework import serializers

from files_management.models import (
    ExternalFileLink,
    FileAttachment,
    FileDownloadLog,
    ManagedFile,
)


class ManagedFileListSerializer(serializers.ModelSerializer):
    """
    Compact file representation for dashboards.
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
            "is_public",
            "created_at",
        ]


class ExternalFileLinkListSerializer(serializers.ModelSerializer):
    """
    Compact external link representation.
    """

    class Meta:
        model = ExternalFileLink
        fields = [
            "id",
            "title",
            "url",
            "provider",
            "review_status",
            "is_active",
            "created_at",
        ]


class FileAttachmentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed attachment representation.
    """

    managed_file = ManagedFileListSerializer(read_only=True)
    external_link = ExternalFileLinkListSerializer(read_only=True)

    class Meta:
        model = FileAttachment
        fields = [
            "id",
            "managed_file",
            "external_link",
            "purpose",
            "visibility",
            "is_primary",
            "is_active",
            "display_name",
            "metadata",
            "attached_at",
        ]


class FileDownloadLogSerializer(serializers.ModelSerializer):
    """
    File download log representation.
    """

    class Meta:
        model = FileDownloadLog
        fields = [
            "id",
            "file",
            "downloaded_by",
            "ip_address",
            "user_agent",
            "downloaded_at",
        ]