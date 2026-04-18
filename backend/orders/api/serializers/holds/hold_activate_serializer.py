from __future__ import annotations

from rest_framework import serializers


class HoldActivateSerializer(serializers.Serializer):
    """
    Validate hold activation payload.
    """

    remaining_seconds = serializers.IntegerField(min_value=0)
    internal_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=4000,
    )