from __future__ import annotations

from rest_framework import serializers


class DisputeResolveSerializer(serializers.Serializer):
    """
    Validate dispute resolution payload.
    """

    outcome = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=64,
    )
    resolution_summary = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=4000,
    )
    internal_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=4000,
    )