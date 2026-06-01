from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants.special_order import (
    SpecialOrderDifficultyLevel,
    SpecialOrderWriterLevel,
    SpecialOrderClientTier,
)

class PredefinedSpecialOrderConfig(TimeStampedModel):
    """
    Tenant-scoped configuration for fixed-price special orders.

    Examples:
        - Shadow Health assignment
        - Poster design
        - SPSS data analysis package
        - Nursing care plan package
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="predefined_special_order_configs",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    requires_full_payment = models.BooleanField(
        default=True,
        help_text=(
            "If true, this fixed special order must be fully paid before "
            "staffing or delivery."
        ),
    )
    allow_wallet_payment = models.BooleanField(default=True)
    allow_external_payment = models.BooleanField(default=True)
    allow_discounts = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_special_order_configs",
    )

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["website", "slug"],
                name="unique_special_order_config_slug_per_website",
            ),
            models.UniqueConstraint(
                fields=["website", "name"],
                name="unique_special_order_config_name_per_website",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "is_active"]),
            models.Index(fields=["website", "slug"]),
        ]

    def __str__(self) -> str:
        return self.name

    if TYPE_CHECKING:
        id: int


class PredefinedSpecialOrderDuration(TimeStampedModel):
    """
    Duration-based price for a fixed special order config.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="predefined_special_order_durations",
    )
    predefined_order = models.ForeignKey(
        "special_orders.PredefinedSpecialOrderConfig",
        on_delete=models.CASCADE,
        related_name="durations",
    )
    duration_days = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    is_active = models.BooleanField(default=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("duration_days",)
        constraints = [
            models.UniqueConstraint(
                fields=["predefined_order", "duration_days"],
                name="unique_special_order_duration_per_config",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "duration_days"]),
            models.Index(fields=["predefined_order", "is_active"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.predefined_order.name} - "
            f"{self.duration_days} days - {self.price}"
        )

    if TYPE_CHECKING:
        id: int


class EstimatedSpecialOrderSettings(TimeStampedModel):
    """
    Tenant-scoped settings for quoted or estimated special orders.

    These settings guide quote creation, deposits, expiry, and milestone
    behavior. Final accepted quotes should still be snapshotted.
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="estimated_special_order_settings",
    )

    default_deposit_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("50.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )
    minimum_deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    allow_installments = models.BooleanField(default=True)
    require_deposit_before_staffing = models.BooleanField(default=True)
    require_full_payment_before_delivery = models.BooleanField(default=True)

    quote_expiry_hours = models.PositiveIntegerField(default=72)

    allow_wallet_payment = models.BooleanField(default=True)
    allow_external_payment = models.BooleanField(default=True)
    allow_discounts = models.BooleanField(default=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("website_id",)
        indexes = [
            models.Index(fields=["website"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.website} - Deposit "
            f"{self.default_deposit_percentage}%"
        )

    if TYPE_CHECKING:
        id: int


class SpecialOrderMilestoneTemplate(TimeStampedModel):
    """
    Optional reusable milestone template for estimated special orders.

    Example:
        - Deposit: 50%
        - Draft checkpoint: 25%
        - Final delivery: 25%
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_milestone_templates",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["website", "name"],
                name="unique_special_order_milestone_template_name",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name

    if TYPE_CHECKING:
        id: int


class SpecialOrderMilestoneTemplateItem(TimeStampedModel):
    """
    One item inside a reusable milestone template.
    """

    template = models.ForeignKey(
        "special_orders.SpecialOrderMilestoneTemplate",
        on_delete=models.CASCADE,
        related_name="items",
    )
    sequence = models.PositiveIntegerField()
    label = models.CharField(max_length=255)
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )

    required_before_staffing = models.BooleanField(default=False)
    required_before_delivery = models.BooleanField(default=False)

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("sequence",)
        constraints = [
            models.UniqueConstraint(
                fields=["template", "sequence"],
                name="unique_special_order_template_item_sequence",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.template.name} - {self.label}"

    if TYPE_CHECKING:
        id: int


class SpecialOrderWriterPayRule(TimeStampedModel):
    """
    Tenant-scoped default writer pay rule for special orders.

    This is only configuration. Actual writer earnings should be posted
    through writer wallet and ledger services.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_writer_pay_rules",
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    fixed_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("100.00")),
        ],
    )

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["website", "name"],
                name="unique_special_order_writer_pay_rule_name",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name

    if TYPE_CHECKING:
        id: int


class SpecialOrderPlatformDifficultyRule(TimeStampedModel):
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_difficulty_rules",
    )
    predefined_order = models.ForeignKey(
        "special_orders.PredefinedSpecialOrderConfig",
        on_delete=models.CASCADE,
        related_name="difficulty_rules",
    )

    platform = models.CharField(max_length=80)
    difficulty_level = models.CharField(
        max_length=50,
        choices=SpecialOrderDifficultyLevel.CHOICES,
    )
    multiplier = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("1.00"),
    )
    is_active = models.BooleanField(default=True)


class SpecialOrderRushSurchargeRule(TimeStampedModel):
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_rush_rules",
    )
    predefined_order = models.ForeignKey(
        "special_orders.PredefinedSpecialOrderConfig",
        on_delete=models.CASCADE,
        related_name="rush_rules",
    )

    max_duration_days = models.PositiveIntegerField()
    surcharge_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_active = models.BooleanField(default=True)


class SpecialOrderWriterLevelSurchargeRule(TimeStampedModel):
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_writer_level_rules",
    )
    predefined_order = models.ForeignKey(
        "special_orders.PredefinedSpecialOrderConfig",
        on_delete=models.CASCADE,
        related_name="writer_level_rules",
    )

    writer_level = models.CharField(
        max_length=50,
        choices=SpecialOrderWriterLevel.CHOICES,
    )
    surcharge_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_active = models.BooleanField(default=True)


class SpecialOrderClientTierDiscountRule(TimeStampedModel):
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_client_tier_rules",
    )
    predefined_order = models.ForeignKey(
        "special_orders.PredefinedSpecialOrderConfig",
        on_delete=models.CASCADE,
        related_name="client_tier_rules",
    )

    client_tier = models.CharField(
        max_length=50,
        choices=SpecialOrderClientTier.CHOICES,
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_active = models.BooleanField(default=True)


class SpecialOrderCurrencyPriceOverride(TimeStampedModel):
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_currency_overrides",
    )
    duration = models.ForeignKey(
        "special_orders.PredefinedSpecialOrderDuration",
        on_delete=models.CASCADE,
        related_name="currency_overrides",
    )

    currency = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)


class SpecialOrderCapacityRule(TimeStampedModel):
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_capacity_rules",
    )
    predefined_order = models.ForeignKey(
        "special_orders.PredefinedSpecialOrderConfig",
        on_delete=models.CASCADE,
        related_name="capacity_rules",
    )

    duration_days = models.PositiveIntegerField()
    max_active_orders = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)