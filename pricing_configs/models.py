from django.db import models
from websites.models import Website

class PricingConfiguration(models.Model):
    """
    Configuration for pricing rules specific to each website.
    """
    base_price_per_page = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Base price per page (USD)."
    )
    base_price_per_slide = models.DecimalField(
        max_digits=10, decimal_places=2, 
        help_text="Base price per slide (USD)."
    )
    technical_order_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Multiplier for technical subjects (e.g., 1.5x for technical)."
    )
    non_technical_order_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Multiplier for non-technical subjects (e.g., 1.0x for non-technical)."
    )
    preferred_writer_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Additional cost for selecting a preferred writer."
    )
    urgent_order_threshold = models.PositiveIntegerField(
        default=8, 
        help_text="Urgent order threshold in hours. The deadline that's considered urgent",
    )
    urgent_order_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.2,
        help_text="Multiplier for urgent orders (e.g., 1.2x for urgent).",
    )
    hvo_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=100,
        help_text="High-value order threshold (total cost).",
    )
    hvo_additional_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Additional cost added to high-value orders.",
    )
    long_deadline_flat_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Flat fee for orders with deadlines longer than 30 days."
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="pricing_configurations_for_websites",
        help_text=("Website-specific pricing configuration."),
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
    Model to store additional services and their pricing.
    """
    name = models.CharField(max_length=100, help_text="Name of the additional service (e.g., Plagiarism Report).")
    description = models.TextField(blank=True, help_text="Description of the service.")
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost of the service (USD).")
    is_active = models.BooleanField(default=True, help_text="Whether this service is currently active.")
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="additional_service_pricing_configs"
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
        return f"{self.name} - ${self.cost} (Website: {self.website})"

    class Meta:
        verbose_name = "Additional Service"
        verbose_name_plural = "Additional Services"

class WriterQuality(models.Model):
    """
    Writer quality levels and associated costs.
    """
    name = models.CharField(max_length=100, help_text="Name of the writer quality level (e.g., Beginner, Expert).")
    description = models.TextField(blank=True, help_text="Description of the writer quality level.")
    cost_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2, 
        help_text="Multiplier applied to base price for this quality level (e.g., 1.5x for Expert)."
    )
    minimum_rating = models.DecimalField(
        max_digits=3, decimal_places=1, default=0.0,
        help_text="Minimum average rating required for this quality level (e.g., 4.5)."
    )
    minimum_completed_orders = models.PositiveIntegerField(
        default=0, help_text="Minimum number of completed orders required for this level."
    )
    max_orders_limit = models.PositiveIntegerField(
        default=0, help_text="Maximum number of orders a writer at this level can take simultaneously."
    )
    # ****To Check if fee is relevant****
    urgent_order_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0,
        help_text="Additional cost for urgent orders for this quality level."
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="writer_quality_pricing_configs"
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
        return f"{self.name} - Multiplier: {self.cost_multiplier}"

    class Meta:
        verbose_name = "Writer Quality"
        verbose_name_plural = "Writer Qualities"


class AcademicLevelPricing(models.Model):
    """
    Represents the pricing configuration based on academic levels.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="academic_level_pricing",
        help_text=("Website this pricing configuration applies to."),
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=("Name of the academic level (e.g., High School, Undergraduate, Master’s, PhD)."),
    )
    multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text=("Multiplier applied to base order pricing for this academic level."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text=("Optional description of this academic level."),
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
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Multiplier: {self.multiplier})"