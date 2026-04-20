"""
Admin-facing pricing config serializers for the order_pricing_core app.
"""

from __future__ import annotations

from rest_framework import serializers

from order_pricing_core.constants import AnalysisLevel
from order_pricing_core.constants import DiagramComplexity


class WebsitePricingProfileSerializer(serializers.Serializer):
    """
    Serializer for website pricing profile updates.
    """

    profile_name = serializers.CharField(required=False)
    currency = serializers.CharField(required=False)

    base_price_per_page = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )
    base_price_per_slide = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )
    base_price_per_diagram = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )

    double_spacing_multiplier = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
        required=False,
    )
    single_spacing_multiplier = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
        required=False,
    )

    preferred_writer_fee = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )

    minimum_paper_order_charge = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )
    minimum_design_order_charge = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )
    minimum_diagram_order_charge = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
    )

    max_pages_per_hour = serializers.IntegerField(required=False, min_value=1)
    extra_hour_per_extra_page = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    rush_recommendation_only = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    allow_customization = serializers.BooleanField(required=False)


class BaseDimensionSerializer(serializers.Serializer):
    """
    Base serializer for website-scoped dimension records.
    """

    code = serializers.CharField()
    label = serializers.CharField()
    sort_order = serializers.IntegerField(required=False, default=0)
    is_active = serializers.BooleanField(required=False, default=True)


class MultiplierDimensionSerializer(BaseDimensionSerializer):
    """
    Serializer for multiplier-based dimensions.
    """

    multiplier = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
    )


class AcademicLevelRateSerializer(MultiplierDimensionSerializer):
    """
    Serializer for academic level rates.
    """


class PaperTypeRateSerializer(MultiplierDimensionSerializer):
    """
    Serializer for paper type rates.
    """


class WorkTypeRateSerializer(MultiplierDimensionSerializer):
    """
    Serializer for work type rates.
    """


class SubjectCategorySerializer(MultiplierDimensionSerializer):
    """
    Serializer for subject category rates.
    """


class SubjectRateSerializer(BaseDimensionSerializer):
    """
    Serializer for subject rates.
    """

    category_id = serializers.IntegerField()
    custom_multiplier = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
        required=False,
        allow_null=True,
    )


class DeadlineRateSerializer(serializers.Serializer):
    """
    Serializer for deadline rate bands.
    """

    label = serializers.CharField()
    max_hours = serializers.IntegerField(min_value=1)
    multiplier = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    sort_order = serializers.IntegerField(required=False, default=0)
    is_active = serializers.BooleanField(required=False, default=True)


class WriterLevelRateSerializer(BaseDimensionSerializer):
    """
    Serializer for writer level rates.
    """

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    is_flat_fee = serializers.BooleanField(required=False, default=True)


class AnalysisLevelRateSerializer(serializers.Serializer):
    """
    Serializer for analysis level rates.
    """

    level = serializers.ChoiceField(choices=AnalysisLevel.CHOICES)
    multiplier = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    is_active = serializers.BooleanField(required=False, default=True)


class DiagramComplexityRateSerializer(serializers.Serializer):
    """
    Serializer for diagram complexity rates.
    """

    complexity = serializers.ChoiceField(
        choices=DiagramComplexity.CHOICES
    )
    multiplier = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
    )
    is_active = serializers.BooleanField(required=False, default=True)