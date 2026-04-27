from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from billing.models.payment_request import PaymentRequest
from billing.constants import PaymentRequestStatus


class PaymentRequestSummarySerializer(serializers.ModelSerializer):
    """
    Serialize a client-safe payment request summary.

    This serializer is intended for client-facing payment request
    visibility.
    """

    remaining_balance = serializers.SerializerMethodField()
    is_fully_paid = serializers.SerializerMethodField()

    class Meta:
        """
        Configure serializer fields for client payment request summary
        reads.
        """

        model = PaymentRequest
        fields = [
            "id",
            "reference",
            "title",
            "description",
            "amount",
            "currency",
            "status",
            "due_at",
            "issued_at",
            "paid_at",
            "payment_intent_reference",
            "remaining_balance",
            "is_fully_paid",
        ]
        read_only_fields = fields

    def get_remaining_balance(self, obj: PaymentRequest) -> Decimal:
        """
        Return remaining payment request balance.

        Args:
            obj:
                Payment request being serialized.

        Returns:
            Decimal:
                Remaining balance.
        """
        if obj.status == PaymentRequestStatus.PAID:
            return Decimal("0.00")
        return obj.amount

    def get_is_fully_paid(self, obj: PaymentRequest) -> bool:
        """
        Return whether the payment request is fully paid.

        Args:
            obj:
                Payment request being serialized.

        Returns:
            bool:
                True when the payment request is fully paid.
        """
        return obj.status == PaymentRequestStatus.PAID