from __future__ import annotations

from rest_framework import serializers


class CompleteOrderSerializer(serializers.Serializer):
    """
    Validate complete order payload.
    """

    internal_reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )