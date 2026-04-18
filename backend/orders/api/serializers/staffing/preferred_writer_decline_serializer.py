from __future__ import annotations

from rest_framework import serializers


class PreferredWriterDeclineSerializer(serializers.Serializer):
    """
    Validate preferred writer decline payload.

    No payload is required right now.
    """

    pass