from __future__ import annotations

from rest_framework import serializers


class ApproveOrderSerializer(serializers.Serializer):
    """
    Validate explicit order approval payload.

    No payload is currently required, but this serializer provides
    a stable extension point for future options such as approval notes.
    """

    pass