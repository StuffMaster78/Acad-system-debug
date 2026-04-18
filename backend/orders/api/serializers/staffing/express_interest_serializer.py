from __future__ import annotations

from rest_framework import serializers


class ExpressInterestSerializer(serializers.Serializer):
    """
    Validate writer interest submission payload.
    """

    message = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=2000,
    )