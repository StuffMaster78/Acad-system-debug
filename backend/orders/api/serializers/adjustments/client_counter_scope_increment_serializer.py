from __future__ import annotations

from rest_framework import serializers


class ClientCounterScopeIncrementSerializer(serializers.Serializer):
    """
    Validate client counter for scope increment.
    """

    countered_quantity = serializers.IntegerField(min_value=1)
    countered_note = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )