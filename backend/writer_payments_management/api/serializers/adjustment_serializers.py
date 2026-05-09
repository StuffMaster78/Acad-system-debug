from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers


class CreateAdjustmentSerializer(serializers.Serializer):
    website_id = serializers.IntegerField()
    writer_id = serializers.IntegerField()

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    reason = serializers.CharField(
        max_length=500,
    )

    source = serializers.CharField(
        max_length=100,
    )

    idempotency_key = serializers.CharField(
        required=False,
        allow_blank=False,
        max_length=255,
    )

    def validate_amount(self, value: Decimal) -> Decimal:
        if value == Decimal("0.00"):
            raise serializers.ValidationError(
                "Amount cannot be zero."
            )

        return value