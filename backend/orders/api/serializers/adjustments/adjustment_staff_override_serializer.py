from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers


class AdjustmentStaffOverrideSerializer(serializers.Serializer):
    """
    Validate staff override proposal payload.
    """

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    notes = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=2000,
    )