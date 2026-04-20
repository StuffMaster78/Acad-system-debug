"""
Paper order quote serializers.
"""

from __future__ import annotations

from rest_framework import serializers

from order_pricing_core.constants import SpacingMode


class PaperOrderQuoteRequestSerializer(serializers.Serializer):
    """
    Input serializer for paper order quote.
    """

    service_code = serializers.CharField()

    pages = serializers.IntegerField(min_value=1)
    deadline_hours = serializers.IntegerField(min_value=1)

    spacing = serializers.ChoiceField(
        choices=SpacingMode.CHOICES,
        default=SpacingMode.DEFAULT,
    )

    paper_type_code = serializers.CharField()
    work_type_code = serializers.CharField()
    subject_code = serializers.CharField()
    academic_level_code = serializers.CharField()

    analysis_level = serializers.CharField(required=False, allow_blank=True)
    writer_level_code = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    preferred_writer_id = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    selected_addon_codes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )

    topic = serializers.CharField(required=False, allow_blank=True)
    instructions = serializers.CharField(required=False, allow_blank=True)


class PriceLineSerializer(serializers.Serializer):
    """
    Breakdown line serializer.
    """

    line_type = serializers.CharField()
    code = serializers.CharField()
    label = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    metadata = serializers.DictField()


class PaperOrderQuoteResponseSerializer(serializers.Serializer):
    """
    Response serializer for paper order quote.
    """

    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    total = serializers.DecimalField(max_digits=12, decimal_places=2)

    lines = PriceLineSerializer(many=True)

    metadata = serializers.DictField()
    suggestions = serializers.ListField()