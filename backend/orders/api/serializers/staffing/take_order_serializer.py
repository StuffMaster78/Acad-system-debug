from __future__ import annotations

from rest_framework import serializers


class TakeOrderSerializer(serializers.Serializer):
    """
    Validate self take payload.

    No payload is required right now, but this serializer keeps the API
    shape consistent and extensible.
    """

    pass