"""
Module for storing the pricing configurations for each website
"""

from django.db import models
from websites.models import Website
from order_configs.models import AcademicLevel
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)


class WriterLevelOptionConfig(models.Model):
    """ 
    Represents different pricing options for writer levels.
    Each option can be a fixed price or a multiplier based on the pricing type.
    This allows for flexible pricing configurations per website.
    Example: $10 for Top 10 writers
    """
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_level_options"
    )
    name = models.CharField(
        max_length=50,
        help_text="Label shown to clients (e.g., Top 10, Advanced)"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Fixed price or multiplier based on pricing_type"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional client-facing note"
    )
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "website")
        ordering = ["sort_order", "name"]
        verbose_name = "Writer Level Option"
        verbose_name_plural = "Writer Level Options"

    def __str__(self):
        return (
            f"{self.name} ({self.website.domain}): "
            f"{self.value}"
        )

class PreferredWriterConfig(models.Model):
    """
    Admin-defined setting for a client choosing to work
    with a preferred writer they worked with before.
    This is a website-level configuration that applies to all writers.
    """
    website = models.OneToOneField(
        Website,
        on_delete=models.CASCADE,
        related_name="preferred_writer_config",
        unique=True,
        help_text="Website this configuration applies to"
    )
    preferred_writer_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Extra cost (in USD) for selecting a preferred writer (applies to all writers)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether preferred writer option is enabled for this website"
    )

    class Meta:
        ordering = ["website"]

    def __str__(self):
        return (
            f"Preferred Writer Config - "
            f"({self.website.domain})"
        )


class PricingConfiguration(models.Model):
    """
     Base configuration per website defining price per page/slide,
    technical multipliers, and other global pricing anchors.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="pricing_configurations_for_websites",
        help_text=("Website-specific pricing configuration."),
    )
    base_price_per_page = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Base price per page (USD)."
    )
    base_price_per_slide = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Base price per slide (USD)."
    )
    technical_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text=(
            "Multiplier for technical subjects (e.g., 1.5x for technical.)"
        )
    )
    non_technical_order_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text=(
            "Multiplier for non-technical subjects"
            "(e.g., 1.0x for non-technical)."
        )
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=("Timestamp when the pricing was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=("Timestamp when the pricing was last updated."),
    )

    def __str__(self):
        return f"Pricing Configuration for {self.website}"

    class Meta:
        verbose_name = "Pricing Configuration"
        verbose_name_plural = "Pricing Configurations"


class AdditionalService(models.Model):
    """
    Add-on upsell services (e.g., plagiarism report, abstract, etc.)
    """
    service_name = models.CharField(
        max_length=100,
        help_text=(
            "Name of the additional service (e.g., Plagiarism Report)."
        )
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the service."
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Cost of the service (USD)."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this service is currently active."
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="additional_service_pricing_configs"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Unique slug for the service (used in URLs)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=("Timestamp when the pricing was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=("Timestamp when the pricing was last updated."),
    )
    def __str__(self):
        return f"{self.service_name} - ${self.cost} (Website: {self.website})"

    class Meta:
        verbose_name = "Additional Service"
        verbose_name_plural = "Additional Services"


class AcademicLevelPricing(models.Model):
    """
    Multiplier pricing per academic level (e.g., Undergrad = 1.0x, PhD = 1.5x).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="website_for_academic_level_pricing",
        help_text=("Website this pricing configuration applies to."),
    )
    academic_level = models.OneToOneField( 
        AcademicLevel,
        on_delete=models.CASCADE,
        related_name="pricing_for_academic_level",
        help_text="Academic Level this pricing applies to."
    )

    multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text=(
            "Multiplier applied to base order pricing for this academic level."
        ),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    level_name = models.CharField(
        max_length=100,
        help_text="Name of the academic level (e.g., Undergraduate, Graduate, PhD)."
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="Unique slug for the academic level (used in URLs)."
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of the academic level."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=("Timestamp when the pricing was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=("Timestamp when the pricing was last updated."),
    )

    class Meta:
        verbose_name =("Academic Level Pricing")
        verbose_name_plural =("Academic Level Pricing")
        ordering = ['website', 'academic_level']

    def __str__(self):
        return f"{self.academic_level.name} (Multiplier: {self.multiplier})"
    


class DeadlineMultiplier(models.Model):
    """ 
    Price multipliers based on deadline windows (e.g., 24h = 1.5x).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="deadline_multipliers"
    )
    label   = models.CharField(
        max_length=100,
        help_text="Label for the deadline (e.g., '1 Hour', '1 Day', '2 Days')."
    )
    hours = models.PositiveIntegerField(
        help_text="Deadline in hours (e.g. 24 hours for a day, 48 for 2 days, etc.)"
    )
    multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Multiplier for this deadline (e.g., 1.3 for 24h)",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hours}h => {self.multiplier}x ({self.website})"
    
    def clean(self):
        """Validate the deadline multiplier configuration."""
        from pricing_configs.services.deadline_multiplier_service import DeadlineMultiplierService
        errors = DeadlineMultiplierService.validate_multiplier_config(
            website=self.website,
            hours=self.hours,
            multiplier=self.multiplier,
            exclude_id=self.id if self.pk else None
        )
        if errors:
            from django.core.exceptions import ValidationError
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_formatted_multiplier(self) -> str:
        """Return formatted multiplier string (e.g., '1.5x')."""
        return f"{self.multiplier}x"
    
    def get_days(self) -> float:
        """Return hours converted to days."""
        return self.hours / 24.0
    
    def is_urgent(self, threshold_hours: int = 24) -> bool:
        """Check if this deadline is considered urgent."""
        return self.hours <= threshold_hours

    class Meta:
        verbose_name = "Deadline Multiplier"
        verbose_name_plural = "Deadline Multipliers"
        unique_together = ("website", "hours")
        ordering = ["website", "hours"]

class TypeOfWorkMultiplier(models.Model):
    """
    Admin-defined multipliers by order type (e.g., Lab Report = 1.4x, Writing From Scratch = 1.2x).
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_type_multipliers"
    )
    name = models.CharField(
        max_length=100,
        help_text="Type of work (e.g., Technical Writing, Lab Report, etc.)"
    )
    multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Multiplier applied to base price for this work type.",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the work type."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=("Timestamp when the multiplier was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=("Timestamp when the multiplier was last updated."),
    )

    def __str__(self):
        return f"{self.name} - x{self.multiplier} ({self.website.domain})"
    class Meta:
        verbose_name = "Order Type Multiplier"
        verbose_name_plural = "Order Type Multipliers"
        unique_together = ['website', 'name']
        ordering = ["website", "name", "multiplier"]