from rest_framework import serializers
from .models import Refund, RefundLog, RefundReceipt


class RefundSerializer(serializers.ModelSerializer):
    total_amount = serializers.SerializerMethodField()

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
        ]
        read_only_fields = fields