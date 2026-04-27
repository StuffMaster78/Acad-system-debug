from __future__ import annotations

from rest_framework import serializers

from billing.models.invoice import Invoice


class InvoiceReadSerializer(serializers.ModelSerializer):
    """
    Serialize invoice records for read operations.

    This serializer is intended for listing and retrieving invoices.
    It does not perform invoice creation or mutation.
    """

    class Meta:
        """
        Configure serializer fields for invoice reads.
        """

        model = Invoice
        fields = [
            "id",
            "reference",
            "title",
            "purpose",
            "description",
            "amount",
            "currency",
            "status",
            "client",
            "recipient_email",
            "recipient_name",
            "issued_by",
            "order_number",
            "order",
            "special_order",
            "class_purchase",
            "payment_intent_reference",
            "payment_token",
            "token_expires_at",
            "custom_payment_link",
            "email_sent_at",
            "email_sent_count",
            "issued_at",
            "due_at",
            "paid_at",
            "cancelled_at",
            "expired_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class InvoiceCreateSerializer(serializers.Serializer):
    """
    Validate payload for creating a draft invoice.

    This serializer validates request shape only. Business logic remains
    in service and orchestration layers.
    """

    title = serializers.CharField(max_length=200)
    purpose = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)
    recipient_email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )
    recipient_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    due_at = serializers.DateTimeField()
    currency = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10,
    )
    order_number = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )
    custom_payment_link = serializers.URLField(
        required=False,
        allow_blank=True,
    )
    order = serializers.IntegerField(required=False, allow_null=True)
    special_order = serializers.IntegerField(
        required=False,
        allow_null=True,
    )
    class_purchase = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    def validate(self, attrs: dict) -> dict:
        """
        Validate high-level invoice create payload consistency.

        Args:
            attrs:
                Incoming serializer attributes.

        Returns:
            dict:
                Validated attributes.

        Raises:
            serializers.ValidationError:
                Raised when mutually conflicting linked objects are
                provided.
        """
        linked_ids = [
            attrs.get("order"),
            attrs.get("special_order"),
            attrs.get("class_purchase"),
        ]
        linked_count = sum(1 for value in linked_ids if value is not None)

        if linked_count > 1:
            raise serializers.ValidationError(
                "Only one linked billable object may be provided."
            )

        return attrs


class InvoiceIssueSerializer(serializers.Serializer):
    """
    Validate payload for issuing an invoice.

    This serializer exists mainly for consistency and future expansion.
    """

    send_notification = serializers.BooleanField(default=False)


class InvoicePreparePaymentSerializer(serializers.Serializer):
    """
    Validate payload for preparing payment for an invoice.
    """

    provider = serializers.CharField(max_length=100)
    generate_token = serializers.BooleanField(default=True)
    token_expiry_hours = serializers.IntegerField(default=72, min_value=1)
    send_notification = serializers.BooleanField(default=False)