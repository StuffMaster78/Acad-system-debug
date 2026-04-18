from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers


class AdjustmentApplyPaymentSerializer(serializers.Serializer):
    """
    Validate incoming payment application payload.
    """

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    external_reference = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )