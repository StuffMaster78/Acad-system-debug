from __future__ import annotations

from rest_framework import serializers


class DisputeEscalateSerializer(serializers.Serializer):
    """
    Validate dispute escalation payload.
    """

    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=4000,
    )