from __future__ import annotations

from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from refunds.models import Refund, RefundLog, RefundReceipt


class RefundSerializer(serializers.ModelSerializer):
    """Serializer for refund workflow records."""

    total_amount = serializers.SerializerMethodField(read_only=True)
    refundable_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Refund
        fields = [
            "id",
            "order_payment",
            "payment_refund",
            "order",
            "client",
            "website",
            "type",
            "wallet_amount",
            "external_amount",
            "refund_method",
            "reason",
            "processed_by",
            "processed_at",
            "status",
            "metadata",
            "error_message",
            "total_amount",
            "refundable_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "payment_refund",
            "order",
            "client",
            "website",
            "refund_method",
            "processed_by",
            "processed_at",
            "status",
            "error_message",
            "total_amount",
            "refundable_amount",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "type": {"required": False},
            "reason": {"required": False},
            "metadata": {"required": False},
        }

    def get_total_amount(self, obj: Refund) -> str:
        return str(obj.total_amount())

    def get_refundable_amount(self, obj: Refund) -> str:
        return str(self._refundable_amount(obj.order_payment))

    def validate(self, attrs):
        request = self.context.get("request")
        payment = attrs.get("order_payment")
        wallet_amount = attrs.get("wallet_amount", Decimal("0.00"))
        external_amount = attrs.get("external_amount", Decimal("0.00"))

        if payment is None:
            raise serializers.ValidationError(
                {"order_payment": "This field is required."}
            )

        total = wallet_amount + external_amount
        if wallet_amount < Decimal("0.00"):
            raise serializers.ValidationError(
                {"wallet_amount": "Refund amount cannot be negative."}
            )
        if external_amount < Decimal("0.00"):
            raise serializers.ValidationError(
                {"external_amount": "Refund amount cannot be negative."}
            )
        if total <= Decimal("0.00"):
            raise serializers.ValidationError(
                "At least one refund amount must be greater than zero."
            )
        if total > self._refundable_amount(payment):
            raise serializers.ValidationError(
                "Refund exceeds refundable balance."
            )

        if request and not request.user.is_staff:
            if payment.client_id != request.user.pk:
                raise serializers.ValidationError(
                    "You can only request refunds for your own payments."
                )

        return attrs

    def create(self, validated_data):
        payment = validated_data["order_payment"]
        validated_data["client"] = payment.client
        validated_data["website"] = payment.website

        payable = getattr(payment, "payable", None)
        if payable is not None:
            if payable.__class__._meta.label_lower == "orders.order":
                validated_data["order"] = payable

        refund = Refund(**validated_data)
        refund.full_clean()
        refund.save()
        return refund

    @staticmethod
    def _refundable_amount(payment) -> Decimal:
        reserved = (
            Refund.objects.filter(
                order_payment=payment,
                status=Refund.PENDING,
            )
            .aggregate(
                wallet_total=Sum("wallet_amount"),
                external_total=Sum("external_amount"),
            )
        )
        wallet_total = reserved["wallet_total"] or Decimal("0.00")
        external_total = reserved["external_total"] or Decimal("0.00")
        remaining = (
            payment.amount
            - payment.amount_refunded
            - wallet_total
            - external_total
        )
        return max(remaining, Decimal("0.00"))


class RefundLogSerializer(serializers.ModelSerializer):
    """Read-only refund audit serializer."""

    class Meta:
        model = RefundLog
        fields = [
            "id",
            "order",
            "amount",
            "website",
            "source",
            "status",
            "metadata",
            "created_at",
            "refund",
            "client",
            "processed_by",
            "action",
        ]
        read_only_fields = fields


class RefundReceiptSerializer(serializers.ModelSerializer):
    """Read-only refund receipt serializer."""

    class Meta:
        model = RefundReceipt
        fields = [
            "id",
            "website",
            "refund",
            "generated_at",
            "reference_code",
            "amount",
            "order_payment",
            "client",
            "processed_by",
            "reason",
        ]
        read_only_fields = fields
