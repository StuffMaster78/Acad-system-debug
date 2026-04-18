from __future__ import annotations

from rest_framework import serializers


class AssignDirectSerializer(serializers.Serializer):
    """
    Validate direct assignment payload.
    """

    writer_id = serializers.IntegerField(min_value=1)