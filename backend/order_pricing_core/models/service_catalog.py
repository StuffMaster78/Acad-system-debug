"""
Service catalog models for the order_pricing_core app.

These models store the standard orderable services and addons that
can be priced through the normal order pricing flow.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models

from order_pricing_core.constants import DesignPackageType
from order_pricing_core.constants import DesignProductType
from order_pricing_core.constants import DiagramType
from order_pricing_core.constants import PricingStrategy
from order_pricing_core.constants import PricingUnit
from order_pricing_core.constants import ServiceFamily


class ServiceCatalogItem(models.Model):
    """
    Stores a standard orderable service for a website.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="order_pricing_services",
    )
    service_code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    service_family = models.CharField(
        max_length=30,
        choices=ServiceFamily.CHOICES,
    )
    pricing_strategy = models.CharField(
        max_length=20,
        choices=PricingStrategy.CHOICES,
        default=PricingStrategy.FORMULA,
    )
    pricing_unit = models.CharField(
        max_length=20,
        choices=PricingUnit.CHOICES,
    )
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    minimum_charge = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_service_catalog_item"
        ordering = ("sort_order", "id")
        unique_together = ("website", "service_code")

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.website} | {self.name}"


class PaperOrderServiceConfig(models.Model):
    """
    Stores paper-order-specific service settings.
    """

    service = models.OneToOneField(
        ServiceCatalogItem,
        on_delete=models.CASCADE,
        related_name="paper_order_config",
    )
    uses_pages = models.BooleanField(default=True)
    supports_spacing = models.BooleanField(default=True)
    supports_academic_level = models.BooleanField(default=True)
    supports_paper_type = models.BooleanField(default=True)
    supports_work_type = models.BooleanField(default=True)
    supports_subject = models.BooleanField(default=True)
    supports_analysis_level = models.BooleanField(default=True)
    supports_writer_level = models.BooleanField(default=True)
    supports_preferred_writer = models.BooleanField(default=True)
    supports_deadline = models.BooleanField(default=True)
    supports_files = models.BooleanField(default=True)
    supports_topic = models.BooleanField(default=True)
    supports_instructions = models.BooleanField(default=True)
    default_is_public = models.BooleanField(default=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_paper_order_service_config"

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"Paper config for {self.service.name}"
    

class DesignOrderServiceConfig(models.Model):
    """
    Stores design-order-specific service settings.
    """

    service = models.OneToOneField(
        ServiceCatalogItem,
        on_delete=models.CASCADE,
        related_name="design_order_config",
    )
    design_product_type = models.CharField(
        max_length=30,
        choices=DesignProductType.CHOICES,
        blank=True,
    )
    default_package_type = models.CharField(
        max_length=20,
        choices=DesignPackageType.CHOICES,
        blank=True,
    )
    supports_quantity = models.BooleanField(default=False)
    supports_slides = models.BooleanField(default=False)
    supports_deadline = models.BooleanField(default=True)
    supports_files = models.BooleanField(default=True)
    supports_topic = models.BooleanField(default=True)
    supports_instructions = models.BooleanField(default=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_design_order_service_config"

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"Design config for {self.service.name}"


class DiagramOrderServiceConfig(models.Model):
    """
    Stores diagram-order-specific service settings.
    """

    service = models.OneToOneField(
        ServiceCatalogItem,
        on_delete=models.CASCADE,
        related_name="diagram_order_config",
    )
    diagram_type = models.CharField(
        max_length=30,
        choices=DiagramType.CHOICES,
        blank=True,
    )
    supports_quantity = models.BooleanField(default=True)
    supports_complexity = models.BooleanField(default=True)
    supports_deadline = models.BooleanField(default=True)
    supports_files = models.BooleanField(default=True)
    supports_topic = models.BooleanField(default=True)
    supports_instructions = models.BooleanField(default=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_diagram_order_service_config"

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"Diagram config for {self.service.name}"


class ServiceAddon(models.Model):
    """
    Stores optional addons for standard order flow services.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="order_pricing_addons",
    )
    addon_code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    flat_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_service_addon"
        ordering = ("sort_order", "id")
        unique_together = ("website", "addon_code")

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.website} | {self.name}"


class ServiceAddonApplicability(models.Model):
    """
    Stores addon applicability for specific services.
    """

    addon = models.ForeignKey(
        ServiceAddon,
        on_delete=models.CASCADE,
        related_name="service_links",
    )
    service = models.ForeignKey(
        ServiceCatalogItem,
        on_delete=models.CASCADE,
        related_name="addon_links",
    )
    is_required = models.BooleanField(default=False)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_service_addon_applicability"
        unique_together = ("addon", "service")

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.addon} -> {self.service}"