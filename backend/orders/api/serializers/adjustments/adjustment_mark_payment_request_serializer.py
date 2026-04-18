from __future__ import annotations

from rest_framework import serializers


class AdjustmentMarkPaymentRequestSerializer(serializers.Serializer):
    """
    Validate payment request creation payload.
    """

    payment_request_reference = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=255,
    )