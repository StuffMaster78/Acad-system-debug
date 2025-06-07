from rest_framework import serializers
from .models import Refund, RefundLog, RefundReceipt

class RefundSerializer(serializers.ModelSerializer):
    total_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Refund
        fields = [
            "id",
            "order_payment",
            "client",
            "website",
            "type",
            "wallet_amount",
            "external_amount",
            "refund_method",
            "processed_by",
            "processed_at",
            "status",
            "metadata",
            "error_message",
            "total_amount",
        ]
        read_only_fields = [
            "processed_by",
            "processed_at",
            "status",
            "error_message",
            "total_amount",
        ]

    def get_total_amount(self, obj):
        return obj.total_amount()

    def validate(self, data):
        wallet_amount = data.get("wallet_amount", 0)
        external_amount = data.get("external_amount", 0)
        if wallet_amount < 0 or external_amount < 0:
            raise serializers.ValidationError("Refund amounts cannot be negative.")
        if wallet_amount == 0 and external_amount == 0:
            raise serializers.ValidationError("At least one refund amount must be greater than zero.")
        return data

class RefundLogSerializer(serializers.ModelSerializer):
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