"""
Diagram order quote serializers.
"""

from __future__ import annotations

from rest_framework import serializers


class DiagramOrderQuoteRequestSerializer(serializers.Serializer):
    """
    Input serializer for diagram order quote.
    """

    service_code = serializers.CharField()

    quantity = serializers.IntegerField(min_value=1)
    deadline_hours = serializers.IntegerField(
        required=False,
        min_value=1,
    )

    diagram_type = serializers.CharField()
    diagram_complexity = serializers.CharField()

    selected_addon_codes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )


class DiagramOrderQuoteResponseSerializer(serializers.Serializer):
    """
    Response serializer for diagram order quote.
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