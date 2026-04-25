from __future__ import annotations

from rest_framework import serializers


class OrderArchiveActionSerializer(serializers.Serializer):
    """
    Validate input for explicit order archival actions.
    """

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
        max_length=1000,
        default="",
    )