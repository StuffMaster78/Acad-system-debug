from __future__ import annotations

from rest_framework import serializers


class ClientAcceptExtraServiceSerializer(serializers.Serializer):
    """
    Validate client acceptance of extra service.
    """

    confirm = serializers.BooleanField(default=True)