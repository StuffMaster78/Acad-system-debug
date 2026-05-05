from __future__ import annotations

from rest_framework import serializers

from special_orders.models import SpecialOrderAdminOverride


class RequestAdminOverrideSerializer(serializers.Serializer):
    override_type = serializers.CharField(max_length=50)
    reason = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    metadata = serializers.DictField(required=False)


class RejectAdminOverrideSerializer(serializers.Serializer):
    reason = serializers.CharField()


class ApplyAdminOverrideSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class AdminOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrderAdminOverride
        fields = [
            "id",
            "special_order",
            "override_type",
            "status",
            "reason",
            "amount",
            "currency",
            "requested_by",
            "approved_by",
            "applied_by",
            "approved_at",
            "applied_at",
            "reversed_at",
            "payment_application",
            "delivery_checkpoint",
            "ledger_entry_reference",
            "metadata",
            "created_at",
            "updated_at",
        ]