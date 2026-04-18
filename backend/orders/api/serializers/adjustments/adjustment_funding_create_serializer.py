from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers


class AdjustmentFundingCreateSerializer(serializers.Serializer):
    """
    Validate funding record creation payload.
    """

    amount_expected = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    payment_request_reference = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )
    invoice_reference = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )