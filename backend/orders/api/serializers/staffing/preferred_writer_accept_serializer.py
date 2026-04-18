from __future__ import annotations

from rest_framework import serializers


class PreferredWriterAcceptSerializer(serializers.Serializer):
    """
    Validate preferred writer acceptance payload.

    No payload is required right now.
    """

    pass