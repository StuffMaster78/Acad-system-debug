from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers


class RequestAdvanceSerializer(serializers.Serializer):
    website_id = serializers.IntegerField()
    writer_id = serializers.IntegerField()

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    reason = serializers.CharField(
        max_length=500,
    )

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Advance amount must be positive."
            )

        return value