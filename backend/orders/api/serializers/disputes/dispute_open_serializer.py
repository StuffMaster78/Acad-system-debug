from __future__ import annotations

from rest_framework import serializers


class DisputeOpenSerializer(serializers.Serializer):
    """
    Validate dispute opening payload.
    """

    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=2000,
    )
    summary = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=4000,
    )