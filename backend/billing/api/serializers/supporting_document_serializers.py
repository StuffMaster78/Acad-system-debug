from __future__ import annotations

from rest_framework import serializers

from billing.models.supporting_document import SupportingDocument


class SupportingDocumentReadSerializer(serializers.ModelSerializer):
    """
    Serialize billing supporting documents for read operations.

    This serializer is intended for listing and retrieving supporting
    document records. It does not perform document creation or mutation.
    """

    class Meta:
        """
        Configure serializer fields for supporting document reads.
        """

        model = SupportingDocument
        fields = [
            "id",
            "invoice",
            "payment_request",
            "file",
            "title",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class SupportingDocumentCreateSerializer(serializers.Serializer):
    """
    Validate payload for creating a billing supporting document.
    """

    file = serializers.FileField()
    title = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )