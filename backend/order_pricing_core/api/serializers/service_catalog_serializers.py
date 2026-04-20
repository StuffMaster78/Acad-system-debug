"""
Admin-facing service catalog serializers for the order_pricing_core app.
"""

from __future__ import annotations

from rest_framework import serializers

from order_pricing_core.constants import DesignPackageType
from order_pricing_core.constants import DesignProductType
from order_pricing_core.constants import DiagramType
from order_pricing_core.constants import PricingStrategy
from order_pricing_core.constants import PricingUnit
from order_pricing_core.constants import ServiceFamily


class ServiceCatalogItemSerializer(serializers.Serializer):
    """
    Serializer for service catalog items.
    """

    service_code = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)

    service_family = serializers.ChoiceField(
        choices=ServiceFamily.CHOICES,
    )
    pricing_strategy = serializers.ChoiceField(
        choices=PricingStrategy.CHOICES,
        default=PricingStrategy.FORMULA,
    )
    pricing_unit = serializers.ChoiceField(
        choices=PricingUnit.CHOICES,
    )

    base_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default="0.00",
    )
    minimum_charge = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default="0.00",
    )

    is_public = serializers.BooleanField(required=False, default=True)
    is_active = serializers.BooleanField(required=False, default=True)
    sort_order = serializers.IntegerField(required=False, default=0)


class PaperOrderServiceConfigSerializer(serializers.Serializer):
    """
    Serializer for paper order service config.
    """

    supports_pages = serializers.BooleanField(required=False, default=True)
    supports_spacing = serializers.BooleanField(required=False, default=True)
    supports_academic_level = serializers.BooleanField(
        required=False,
        default=True,
    )
    supports_paper_type = serializers.BooleanField(
        required=False,
        default=True,
    )
    supports_work_type = serializers.BooleanField(
        required=False,
        default=True,
    )
    supports_subject = serializers.BooleanField(required=False, default=True)
    supports_analysis_level = serializers.BooleanField(
        required=False,
        default=True,
    )
    supports_writer_level = serializers.BooleanField(
        required=False,
        default=True,
    )
    supports_preferred_writer = serializers.BooleanField(
        required=False,
        default=True,
    )
    supports_deadline = serializers.BooleanField(required=False, default=True)
    supports_files = serializers.BooleanField(required=False, default=True)
    supports_topic = serializers.BooleanField(required=False, default=True)
    supports_instructions = serializers.BooleanField(
        required=False,
        default=True,
    )
    default_is_public = serializers.BooleanField(
        required=False,
        default=True,
    )


class DesignOrderServiceConfigSerializer(serializers.Serializer):
    """
    Serializer for design order service config.
    """

    design_product_type = serializers.ChoiceField(
        choices=DesignProductType.CHOICES,
        required=False,
        allow_blank=True,
    )
    default_package_type = serializers.ChoiceField(
        choices=DesignPackageType.CHOICES,
        required=False,
        allow_blank=True,
    )
    supports_quantity = serializers.BooleanField(required=False, default=False)
    supports_slides = serializers.BooleanField(required=False, default=False)
    supports_deadline = serializers.BooleanField(required=False, default=True)
    supports_files = serializers.BooleanField(required=False, default=True)
    supports_topic = serializers.BooleanField(required=False, default=True)
    supports_instructions = serializers.BooleanField(
        required=False,
        default=True,
    )


class DiagramOrderServiceConfigSerializer(serializers.Serializer):
    """
    Serializer for diagram order service config.
    """

    diagram_type = serializers.ChoiceField(
        choices=DiagramType.CHOICES,
        required=False,
        allow_blank=True,
    )
    supports_quantity = serializers.BooleanField(required=False, default=True)
    supports_complexity = serializers.BooleanField(
        required=False,
        default=True,
    )
    supports_deadline = serializers.BooleanField(required=False, default=True)
    supports_files = serializers.BooleanField(required=False, default=True)
    supports_topic = serializers.BooleanField(required=False, default=True)
    supports_instructions = serializers.BooleanField(
        required=False,
        default=True,
    )


class ServiceAddonSerializer(serializers.Serializer):
    """
    Serializer for service addons.
    """

    addon_code = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    flat_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    is_public = serializers.BooleanField(required=False, default=True)
    is_active = serializers.BooleanField(required=False, default=True)
    sort_order = serializers.IntegerField(required=False, default=0)