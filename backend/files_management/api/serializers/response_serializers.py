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
            "original_filename",
            "file_size_bytes",
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

    Pass ``downloaded_attachment_ids`` (a set of attachment PKs) in the
    serializer context to enable per-user ``is_new_for_user`` without an
    extra query per file.  The caller is responsible for prefetching.
    """

    managed_file = ManagedFileListSerializer(read_only=True)
    external_link = ExternalFileLinkListSerializer(read_only=True)
    is_new_for_user = serializers.SerializerMethodField()

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
            "is_new_for_user",
        ]

    def get_is_new_for_user(self, obj) -> bool:
        downloaded_ids = self.context.get("downloaded_attachment_ids")
        if downloaded_ids is None:
            return False
        return obj.id not in downloaded_ids


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
