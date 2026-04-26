from __future__ import annotations

from rest_framework import serializers

from files_management.enums import (
    DeletionRequestScope,
    FileAccessAction,
    FilePurpose,
)
from files_management.models import (
    FileAccessGrant,
    FileDeletionRequest,
    FilePolicy,
)


class AdminExternalLinkReviewSerializer(serializers.Serializer):
    """
    Input serializer for staff external link review.
    """

    review_note = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class AdminDeletionReviewSerializer(serializers.Serializer):
    """
    Input serializer for deletion request review.
    """

    admin_comment = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class AdminDeletionRejectSerializer(serializers.Serializer):
    """
    Input serializer for deletion request rejection.
    """

    admin_comment = serializers.CharField()


class AdminDeletionCompleteSerializer(serializers.Serializer):
    """
    Input serializer for completing deletion requests.
    """

    admin_comment = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class FilePolicySerializer(serializers.ModelSerializer):
    """
    Serializer for tenant file policy management.
    """

    class Meta:
        model = FilePolicy
        fields = [
            "id",
            "name",
            "purpose",
            "allowed_mime_types",
            "allowed_extensions",
            "max_file_size_bytes",
            "allow_external_links",
            "external_links_require_review",
            "allowed_external_providers",
            "require_scan_before_download",
            "require_review_before_download",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_purpose(self, value: str) -> str:
        """
        Validate policy purpose.
        """

        valid_values = {item.value for item in FilePurpose}

        if value not in valid_values:
            raise serializers.ValidationError("Invalid file purpose.")

        return value


class FileAccessGrantCreateSerializer(serializers.Serializer):
    """
    Serializer for creating explicit file access grants.
    """

    managed_file_id = serializers.IntegerField()
    grantee_id = serializers.IntegerField()
    attachment_id = serializers.IntegerField(required=False)
    action = serializers.ChoiceField(choices=FileAccessAction.choices)
    reason = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False)


class FileAccessGrantSerializer(serializers.ModelSerializer):
    """
    Read serializer for explicit file access grants.
    """

    class Meta:
        model = FileAccessGrant
        fields = [
            "id",
            "managed_file",
            "attachment",
            "grantee",
            "granted_by",
            "action",
            "reason",
            "expires_at",
            "revoked_at",
            "revoked_by",
            "created_at",
        ]
        read_only_fields = fields


class FileDeletionRequestAdminSerializer(serializers.ModelSerializer):
    """
    Read serializer for deletion requests.
    """

    class Meta:
        model = FileDeletionRequest
        fields = [
            "id",
            "managed_file",
            "attachment",
            "requested_by",
            "reason",
            "scope",
            "status",
            "reviewed_by",
            "reviewed_at",
            "admin_comment",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def validate_scope(self, value: str) -> str:
        """
        Validate deletion scope.
        """

        valid_values = {item.value for item in DeletionRequestScope}

        if value not in valid_values:
            raise serializers.ValidationError("Invalid deletion scope.")

        return value


class AdminQuarantineReleaseSerializer(serializers.Serializer):
    """
    Input serializer for releasing a quarantined file.
    """

    summary = serializers.CharField(required=False, allow_blank=True)