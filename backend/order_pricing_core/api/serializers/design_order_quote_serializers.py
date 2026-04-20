"""
Design order quote serializers.
"""

from __future__ import annotations

from rest_framework import serializers


class DesignOrderQuoteRequestSerializer(serializers.Serializer):
    """
    Input serializer for design order quote.
    """

    service_code = serializers.CharField()

    slides = serializers.IntegerField(required=False, min_value=1)
    quantity = serializers.IntegerField(required=False, min_value=1)

    deadline_hours = serializers.IntegerField(
        required=False,
        min_value=1,
    )

    selected_addon_codes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )

    topic = serializers.CharField(required=False, allow_blank=True)
    instructions = serializers.CharField(required=False, allow_blank=True)


class DesignOrderQuoteResponseSerializer(serializers.Serializer):
    """
    Response serializer for design order quote.
    """

    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    total = serializers.DecimalField(max_digits=12, decimal_places=2)

    lines = serializers.ListField()
    metadata = serializers.DictField()
    suggestions = serializers.ListField()