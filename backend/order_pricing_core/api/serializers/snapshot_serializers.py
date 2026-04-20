"""
Snapshot serializers for the order_pricing_core app.
"""

from __future__ import annotations

from rest_framework import serializers


class PricingSnapshotCreateSerializer(serializers.Serializer):
    """
    Input serializer for pricing snapshot creation.
    """

    related_object_type = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    related_object_id = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )