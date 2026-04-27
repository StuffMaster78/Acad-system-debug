from __future__ import annotations

from rest_framework import serializers

from billing.models.receipt import Receipt


class ReceiptReadSerializer(serializers.ModelSerializer):
    """
    Serialize receipt records for read operations.

    This serializer is intended for listing and retrieving receipts.
    It does not perform receipt creation or mutation.
    """
    title = serializers.CharField(source="title_snapshot", read_only=True)
    description = serializers.CharField(
        source="description_snapshot",
        read_only=True,
    )
    
    class Meta:
        """
        Configure serializer fields for receipt reads.
        """

        model = Receipt
        fields = [
            "id",
            "reference",
            "client",
            "recipient_email",
            "recipient_name",
            "invoice",
            "payment_request",
            "title_snapshot",
            "description_snapshot",
            "company_name_snapshot",
            "website_name_snapshot",
            "website_domain_snapshot",
            "support_email_snapshot",
            "amount",
            "currency",
            "status",
            "payment_intent_reference",
            "external_reference",
            "payment_provider",
            "issued_at",
            "voided_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields