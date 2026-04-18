from __future__ import annotations

from rest_framework import serializers


class SubmitOrderSerializer(serializers.Serializer):
    """
    Validate submit order payload.

    No payload is required right now.
    """

    pass