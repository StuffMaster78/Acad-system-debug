from __future__ import annotations

from rest_framework import serializers


class ReleaseToPoolSerializer(serializers.Serializer):
    """
    Validate release to pool payload.
    """

    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=2000,
    )