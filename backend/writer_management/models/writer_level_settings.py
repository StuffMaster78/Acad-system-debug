"""
WriterLevelSettings defines all configurable rules for a writer level.

This is NOT a business logic engine.

It is a declarative configuration used by services to:
- calculate earnings
- determine workload limits
- evaluate eligibility thresholds
- apply urgency multipliers

All computations MUST live in services.
"""

from django.db import models
from decimal import Decimal


class WriterLevelSettings(models.Model):
    """
    Configurable ruleset for a writer level.

    This model is read-only from a business logic perspective.
    It acts as a configuration contract.
    """

    writer_level = models.OneToOneField(
        "writer_management.WriterLevel",
        on_delete=models.CASCADE,
        related_name="settings",
    )

    # ---------------------------------------------------
    # EARNINGS CONFIGURATION (PRICING LAYER)
    # ---------------------------------------------------

    base_pay_per_page = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    base_pay_per_slide = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    base_pay_per_chart = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    additional_page_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    additional_slide_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    additional_chart_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # TIP SYSTEM (PASS-THROUGH RULE)
    tip_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        help_text="Percentage of tips writers retain.",
    )

    # ---------------------------------------------------
    # CAPACITY CONFIGURATION (WORKLOAD LAYER)
    # ---------------------------------------------------

    max_active_orders = models.PositiveIntegerField(
        default=0,
        help_text="Maximum concurrent active orders allowed.",
    )

    max_manual_takes = models.PositiveIntegerField(
        default=0,
        help_text="Max orders writer can take manually (non-assigned).",
    )

    max_pending_assignments = models.PositiveIntegerField(
        default=0,
        help_text="Max queued assignments allowed.",
    )

    # ---------------------------------------------------
    # URGENCY CONFIGURATION
    # ---------------------------------------------------

    urgent_time_threshold_hours = models.PositiveIntegerField(
        default=6,
        help_text="Orders below this threshold are treated as urgent.",
    )

    urgent_order_surcharge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    urgent_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Multiplier applied to earnings for urgent orders.",
    )

    # ---------------------------------------------------
    # ELIGIBILITY RULES (PROMOTION / ACCESS CONTROL)
    # ---------------------------------------------------

    min_completed_orders = models.PositiveIntegerField(
        default=0,
    )

    min_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    min_successful_takes = models.PositiveIntegerField(
        default=0,
    )

    min_completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    max_revision_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    max_lateness_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # ---------------------------------------------------
    # STATUS
    # ---------------------------------------------------

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Writer Level Settings"
        verbose_name_plural = "Writer Level Settings"
        indexes = [
            models.Index(fields=["writer_level", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"LevelSettings({self.writer_level.pk})"