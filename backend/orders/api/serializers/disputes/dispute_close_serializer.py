from __future__ import annotations

from rest_framework import serializers


class DisputeCloseSerializer(serializers.Serializer):
    """
    Validate dispute closure payload.
    """

    restore_order_status = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=32,
    )