from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers


class AdjustmentCreateSerializer(serializers.Serializer):
    """
    Validate adjustment request creation payload.
    """

    adjustment_type = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=32,
    )
    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=2000,
    )
    quoted_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    scope_summary = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=4000,
    )