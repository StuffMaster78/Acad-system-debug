from __future__ import annotations

from rest_framework import serializers


class PublicPreparePaymentSerializer(serializers.Serializer):
    """
    Validate payload for public token-based payment preparation.
    """

    provider = serializers.CharField(max_length=100)