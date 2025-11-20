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
        extra_kwargs = {
            "client": {"required": False, "allow_null": True},
            "website": {"required": False, "allow_null": True},
            "type": {"required": False},
            "refund_method": {"required": False},
        }

    def get_total_amount(self, obj):
        return obj.total_amount()

    def validate(self, data):
        wallet_amount = data.get("wallet_amount", 0)
        external_amount = data.get("external_amount", 0)
        order_payment = data.get("order_payment")
        if wallet_amount < 0 or external_amount < 0:
            raise serializers.ValidationError("Refund amounts cannot be negative.")
        if wallet_amount == 0 and external_amount == 0:
            raise serializers.ValidationError("At least one refund amount must be greater than zero.")
        if order_payment:
            total = wallet_amount + external_amount
            paid = getattr(order_payment, "discounted_amount", None) or getattr(order_payment, "original_amount", 0)
            if paid is not None and total > paid:
                raise serializers.ValidationError("Refund exceeds paid amount.")
            # Prevent duplicate refunds (one refund allowed in tests)
            if order_payment.refunds.exists():
                raise serializers.ValidationError("Order payment already refunded.")
        return data

    def create(self, validated_data):
        # Infer client and website from order_payment if not supplied
        order_payment = validated_data.get("order_payment")
        if order_payment is None:
            raise serializers.ValidationError({"order_payment": "This field is required."})

        if not validated_data.get("client"):
            try:
                validated_data["client"] = getattr(order_payment, "client", None)
            except Exception:
                pass
        if not validated_data.get("website"):
            try:
                validated_data["website"] = (
                    getattr(order_payment, "website", None)
                    or getattr(getattr(order_payment, "order", None), "website", None)
                )
            except Exception:
                pass
        return super().create(validated_data)

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
            "processed_at",
            "reason",
        ]
        read_only_fields = fields