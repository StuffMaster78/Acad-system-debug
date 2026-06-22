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
    attached_by_name = serializers.SerializerMethodField()
    attached_by_role = serializers.SerializerMethodField()

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
            # uploader
            "attached_by_name",
            "attached_by_role",
            # delivery tracking
            "is_submitted",
            "delivery_status",
            "submitted_at",
            "first_downloaded_at",
            # revision tracking
            "revision_cycle",
        ]

    def get_is_new_for_user(self, obj) -> bool:
        downloaded_ids = self.context.get("downloaded_attachment_ids")
        if downloaded_ids is None:
            return False
        return obj.id not in downloaded_ids

    def get_attached_by_name(self, obj) -> str | None:
        user = obj.attached_by
        if not user:
            return None
        full = (getattr(user, "get_full_name", None) or (lambda: ""))()
        return full or getattr(user, "email", None) or str(user)

    def get_attached_by_role(self, obj) -> str | None:
        user = obj.attached_by
        return getattr(user, "role", None) if user else None


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
