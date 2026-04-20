"""
Composite quote serializers for the order_pricing_core app.
"""

from __future__ import annotations

from rest_framework import serializers


class CompositeQuoteCreateSerializer(serializers.Serializer):
    """
    Input serializer for creating or updating composite quotes.
    """

    component_session_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
    )


class CompositeQuoteFinalizeSerializer(serializers.Serializer):
    """
    Input serializer for finalizing a composite quote.
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


class CompositeQuoteItemResponseSerializer(serializers.Serializer):
    """
    Response serializer for a composite quote item.
    """

    pricing_quote_session_id = serializers.UUIDField()
    service_code = serializers.CharField()
    service_name = serializers.CharField()
    component_label = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    sort_order = serializers.IntegerField()


class CompositeQuoteResponseSerializer(serializers.Serializer):
    """
    Response serializer for a composite quote.
    """

    session_id = serializers.UUIDField()
    currency = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_final = serializers.BooleanField()
    items = CompositeQuoteItemResponseSerializer(many=True)


class CompositeQuoteFinalizeResponseSerializer(serializers.Serializer):
    """
    Response serializer for finalized composite quote payload.
    """

    session_id = serializers.UUIDField()
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField()
    component_snapshot_ids = serializers.ListField(
        child=serializers.IntegerField(),
    )
    is_final = serializers.BooleanField()