"""
Module for storing the pricing configurations for each website
"""

from django.db import models
from websites.models import Website
from order_configs.models import AcademicLevel
from django.core.validators import MinValueValidator, MaxValueValidator


class PreferredWriterConfig(models.Model):
    """
    Admin-defined preferred writer types and their pricing per website.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="preferred_writer_configs"
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the writer tier (e.g., Advanced, Top 10, Elite Ninja)"
    )
    preferred_writer_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Extra cost (in USD) for selecting this writer tier"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description for this writer tier"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["website", "name"]
        ordering = ["website", "preferred_writer_cost"]

    def __str__(self):
        return f"{self.name} - ${self.cost} ({self.website.domain})"


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
    technical_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Multiplier for technical subjects (e.g., 1.5x for technical)."
    )
    non_technical_order_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Multiplier for non-technical subjects (e.g., 1.0x for non-technical)."
    )
    urgent_order_threshold = models.PositiveIntegerField(
        default=8,
        help_text="Urgent order threshold in hours. The deadline that's considered urgent.",
    )
    hvo_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=100,
        help_text="High-value order threshold (total cost).",
    )

    convenience_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0,
        help_text="Convenience fee applied to all orders (USD) for reducing deadline."
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
    service_name = models.CharField(
        max_length=100,
        help_text="Name of the additional service (e.g., Plagiarism Report)."
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


class WriterQuality(models.Model):
    """
    Writer quality levels and associated costs.
    Example: Beginner, Intermediate, Expert, etc.
    """
    name = models.CharField(
        max_length=100,
        help_text="Name of the writer quality level (e.g., Best-Available, Beginner, Expert)."
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the writer quality level."
    )
    cost_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2, 
        help_text="Multiplier applied to base price for this quality level (e.g., 1.5x for Expert).",
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    minimum_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        help_text="Minimum average rating required for this quality level (e.g., 4.5)."
    )
    minimum_completed_orders = models.PositiveIntegerField(
        default=0, help_text="Minimum number of completed orders required for this level."
    )
    max_orders_limit = models.PositiveIntegerField(
        default=0, help_text="Maximum number of orders a writer at this level can take simultaneously."
    )
    # ****To Check if fee is relevant****
    # **** To check whether we need multiplier or fixed cost***
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
    Example: Undergraduate, Graduate, PhD, etc.
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
        help_text=("Multiplier applied to base order pricing for this academic level."),
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
    """ Represents the deadline multipliers for different deadlines.
    Example: 24 hours, 48 hours, etc.
    This model allows for different multipliers based on the
    deadline set for an order.
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

    class Meta:
        verbose_name = "Deadline Multiplier"
        verbose_name_plural = "Deadline Multipliers"
        unique_together = ("website", "hours")
        ordering = ["website", "hours"]

class OrderTypeMultiplier(models.Model):
    """
    Admin-defined multipliers for different types of work.
    Example: Technical Writing, Proofreading, Lab Reports, etc.
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