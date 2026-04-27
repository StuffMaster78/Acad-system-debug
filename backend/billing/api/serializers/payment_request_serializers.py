from __future__ import annotations

from rest_framework import serializers

from billing.models.payment_request import PaymentRequest


class PaymentRequestReadSerializer(serializers.ModelSerializer):
    """
    Serialize billing payment requests for read operations.

    This serializer is intended for listing and retrieving existing
    payment requests. It does not perform business mutations.
    """

    class Meta:
        """
        Configure serializer fields for read operations.
        """

        model = PaymentRequest
        fields = [
            "id",
            "reference",
            "title",
            "purpose",
            "description",
            "amount",
            "currency",
            "status",
            "recipient_email",
            "recipient_name",
            "order",
            "special_order",
            "class_purchase",
            "invoice",
            "payment_intent_reference",
            "issued_at",
            "due_at",
            "paid_at",
            "cancelled_at",
            "expired_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PaymentRequestCreateSerializer(serializers.Serializer):
    """
    Validate payload for creating a billing payment request.

    This serializer only validates request shape. It does not create the
    payment request directly.
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
    due_at = serializers.DateTimeField(required=False, allow_null=True)
    currency = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10,
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
        Validate high-level create payload consistency.

        Args:
            attrs:
                Incoming serializer attributes.

        Returns:
            dict:
                Validated attributes.

        Raises:
            serializers.ValidationError:
                Raised when mutually conflicting object links are
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


class PaymentRequestIssueSerializer(serializers.Serializer):
    """
    Validate payload for issuing a billing payment request.

    This serializer exists mainly for consistency and future expansion.
    """

    send_notification = serializers.BooleanField(default=False)


class PaymentRequestPreparePaymentSerializer(serializers.Serializer):
    """
    Validate payload for preparing payment for a billing payment request.
    """

    provider = serializers.CharField(max_length=100)
    send_notification = serializers.BooleanField(default=False)