from __future__ import annotations

from rest_framework import serializers


class AdjustmentCancelSerializer(serializers.Serializer):
    """
    Validate adjustment cancel payload.
    """

    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=2000,
    )