"""
Pricing dimension models for the orders_pricing_core app.

These models store website-scoped pricing dimensions used by
services and calculators. Business rules and validation belong in
validators and services.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models

from order_pricing_core.constants import AnalysisLevel
from order_pricing_core.constants import DiagramComplexity


class BaseWebsiteDimension(models.Model):
    """
    Abstract base model for website-scoped pricing dimensions.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
    )
    code = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        abstract = True
        ordering = ("sort_order", "id")

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.website} | {self.label}"


class AcademicLevelRate(BaseWebsiteDimension):
    """
    Stores website-scoped academic level pricing multipliers.
    """

    multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("1.0000"),
    )

    class Meta(BaseWebsiteDimension.Meta):
        """
        Model metadata.
        """

        db_table = "orders_pricing_core_academic_level_rate"
        unique_together = ("website", "code")


class PaperTypeRate(BaseWebsiteDimension):
    """
    Stores website-scoped paper type pricing multipliers.
    """

    multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("1.0000"),
    )

    class Meta(BaseWebsiteDimension.Meta):
        """
        Model metadata.
        """

        db_table = "orders_pricing_core_paper_type_rate"
        unique_together = ("website", "code")


class WorkTypeRate(BaseWebsiteDimension):
    """
    Stores website-scoped work type pricing multipliers.
    """

    multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("1.0000"),
    )

    class Meta(BaseWebsiteDimension.Meta):
        """
        Model metadata.
        """

        db_table = "orders_pricing_core_work_type_rate"
        unique_together = ("website", "code")


class DeadlineRate(models.Model):
    """
    Stores website-scoped deadline pricing bands.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="orders_pricing_deadline_rates",
    )
    label = models.CharField(max_length=100)
    max_hours = models.PositiveIntegerField()
    multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("1.0000"),
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "orders_pricing_core_deadline_rate"
        ordering = ("max_hours", "sort_order", "id")

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.website} | {self.label}"


class SubjectCategory(BaseWebsiteDimension):
    """
    Stores website-scoped subject category multipliers.
    """

    multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("1.0000"),
    )

    class Meta(BaseWebsiteDimension.Meta):
        """
        Model metadata.
        """

        db_table = "orders_pricing_core_subject_category"
        unique_together = ("website", "code")


class SubjectRate(BaseWebsiteDimension):
    """
    Stores website-scoped subjects and their category mapping.
    """

    category = models.ForeignKey(
        SubjectCategory,
        on_delete=models.PROTECT,
        related_name="subjects",
    )
    custom_multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
    )

    class Meta(BaseWebsiteDimension.Meta):
        """
        Model metadata.
        """

        db_table = "orders_pricing_core_subject_rate"
        unique_together = ("website", "code")


class WriterLevelRate(BaseWebsiteDimension):
    """
    Stores website-scoped writer level upsell settings.
    """

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_flat_fee = models.BooleanField(default=True)

    class Meta(BaseWebsiteDimension.Meta):
        """
        Model metadata.
        """

        db_table = "orders_pricing_core_writer_level_rate"
        unique_together = ("website", "code")


class AnalysisLevelRate(models.Model):
    """
    Stores website-scoped analysis level pricing multipliers.

    These rates support work involving calculations, advanced charts,
    Excel deliverables, SPSS outputs, and similar analysis-heavy work.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="orders_pricing_analysis_level_rates",
    )
    level = models.CharField(
        max_length=20,
        choices=AnalysisLevel.CHOICES,
    )
    multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("1.0000"),
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "orders_pricing_core_analysis_level_rate"
        unique_together = ("website", "level")
        ordering = ("id",)

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.website} | {self.level}"


class DiagramComplexityRate(models.Model):
    """
    Stores website-scoped diagram complexity multipliers.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="orders_pricing_diagram_complexity_rates",
    )
    complexity = models.CharField(
        max_length=20,
        choices=DiagramComplexity.CHOICES,
    )
    multiplier = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal("1.0000"),
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "orders_pricing_core_diagram_complexity_rate"
        unique_together = ("website", "complexity")
        ordering = ("id",)

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.website} | {self.complexity}"
