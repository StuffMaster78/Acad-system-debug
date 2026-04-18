from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers


class AdjustmentAcceptSerializer(serializers.Serializer):
    """
    Validate adjustment acceptance payload.
    """

    final_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )