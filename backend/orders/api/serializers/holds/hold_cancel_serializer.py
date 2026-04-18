from __future__ import annotations

from rest_framework import serializers


class HoldCancelSerializer(serializers.Serializer):
    """
    Validate hold cancel payload.
    """

    internal_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=4000,
    )