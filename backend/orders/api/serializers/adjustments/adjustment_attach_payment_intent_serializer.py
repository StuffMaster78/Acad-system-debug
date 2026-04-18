from __future__ import annotations

from rest_framework import serializers


class AdjustmentAttachPaymentIntentSerializer(serializers.Serializer):
    """
    Validate payment intent attachment payload.
    """

    payment_intent_reference = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=255,
    )