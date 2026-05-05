from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from special_orders.models.configs import (
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    SpecialOrderCapacityRule,
    SpecialOrderClientTierDiscountRule,
    SpecialOrderCurrencyPriceOverride,
    SpecialOrderPlatformDifficultyRule,
    SpecialOrderRushSurchargeRule,
    SpecialOrderWriterLevelSurchargeRule,
)


@dataclass(frozen=True)
class FixedSpecialOrderPriceQuote:
    """
    Calculated fixed special order price.
    """

    base_price: Decimal
    gross_amount: Decimal
    currency: str
    line_items: list[dict[str, Any]]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class FixedSpecialOrderGrossQuote:
    base_price: Decimal
    gross_amount: Decimal
    currency: str
    line_items: list[dict[str, Any]]
    metadata: dict[str, Any]

class SpecialOrderFixedPricingService:
    """
    Calculates the gross fixed special order pricing
    from admin-managed rules.
    Discounts are handled by the central discount system.
    """

    @classmethod
    def calculate_gross_price(
        cls,
        *,
        predefined_config: PredefinedSpecialOrderConfig,
        predefined_duration: PredefinedSpecialOrderDuration,
        currency: str = "USD",
        platform: str = "",
        writer_level: str = "",
    ) -> FixedSpecialOrderPriceQuote:
        """
        Calculate final fixed special order price.
        """
        cls._validate_inputs(
            predefined_config=predefined_config,
            predefined_duration=predefined_duration,
        )
        cls._validate_capacity(
            predefined_config=predefined_config,
            predefined_duration=predefined_duration,
        )

        base_price = cls._get_base_price(
            predefined_duration=predefined_duration,
            currency=currency,
        )

        line_items: list[dict[str, Any]] = [
            {
                "code": "base_price",
                "label": "Base price",
                "amount": base_price,
            }
        ]

        running_total = base_price

        difficulty_amount = cls._calculate_platform_difficulty_amount(
            predefined_config=predefined_config,
            platform=platform,
            running_total=running_total,
        )
        if difficulty_amount > Decimal("0.00"):
            running_total += difficulty_amount
            line_items.append(
                {
                    "code": "platform_difficulty",
                    "label": "Platform difficulty",
                    "amount": difficulty_amount,
                }
            )

        rush_amount = cls._calculate_rush_amount(
            predefined_config=predefined_config,
            duration_days=predefined_duration.duration_days,
            running_total=running_total,
        )
        if rush_amount > Decimal("0.00"):
            running_total += rush_amount
            line_items.append(
                {
                    "code": "rush_surcharge",
                    "label": "Rush surcharge",
                    "amount": rush_amount,
                }
            )

        writer_level_amount = cls._calculate_writer_level_amount(
            predefined_config=predefined_config,
            writer_level=writer_level,
            running_total=running_total,
        )
        if writer_level_amount > Decimal("0.00"):
            running_total += writer_level_amount
            line_items.append(
                {
                    "code": "writer_level_surcharge",
                    "label": "Writer level surcharge",
                    "amount": writer_level_amount,
                }
            )


        gross_amount = cls._money(running_total)

        return FixedSpecialOrderPriceQuote(
            base_price=base_price,
            gross_amount=gross_amount,
            currency=currency,
            line_items=[
                {
                    **item,
                    "amount": str(cls._money(item["amount"])),
                }
                for item in line_items
            ],
            metadata={
                "predefined_config_id": predefined_config.id,
                "predefined_duration_id": predefined_duration.id,
                "duration_days": predefined_duration.duration_days,
                "platform": platform,
                "writer_level": writer_level,
            },
        )

    @staticmethod
    def _validate_inputs(
        *,
        predefined_config: PredefinedSpecialOrderConfig,
        predefined_duration: PredefinedSpecialOrderDuration,
    ) -> None:
        """
        Validate config and duration.
        """
        if predefined_config.website.id != predefined_duration.website.id:
            raise ValueError("Config and duration belong to different tenants.")

        if predefined_duration.predefined_order.id != predefined_config.id:
            raise ValueError("Duration does not belong to this config.")

        if not predefined_config.is_active:
            raise ValueError("Predefined special order config is inactive.")

        if not predefined_duration.is_active:
            raise ValueError("Predefined duration is inactive.")

        if predefined_duration.price <= Decimal("0.00"):
            raise ValueError("Predefined duration price must be positive.")

    @classmethod
    def _get_base_price(
        cls,
        *,
        predefined_duration: PredefinedSpecialOrderDuration,
        currency: str,
    ) -> Decimal:
        """
        Return currency override price when available, else duration price.
        """
        override = (
            SpecialOrderCurrencyPriceOverride.objects.filter(
                website=predefined_duration.website,
                duration=predefined_duration,
                currency=currency,
                is_active=True,
            )
            .order_by("-created_at")
            .first()
        )

        if override is not None:
            return cls._money(override.price)

        return cls._money(predefined_duration.price)

    @classmethod
    def _calculate_platform_difficulty_amount(
        cls,
        *,
        predefined_config: PredefinedSpecialOrderConfig,
        platform: str,
        running_total: Decimal,
    ) -> Decimal:
        """
        Calculate platform difficulty amount from multiplier.
        """
        if not platform:
            return Decimal("0.00")

        rule = (
            SpecialOrderPlatformDifficultyRule.objects.filter(
                website=predefined_config.website,
                predefined_order=predefined_config,
                platform=platform,
                is_active=True,
            )
            .order_by("-created_at")
            .first()
        )

        if rule is None:
            return Decimal("0.00")

        if rule.multiplier <= Decimal("1.00"):
            return Decimal("0.00")

        return cls._money(running_total * (rule.multiplier - Decimal("1.00")))

    @classmethod
    def _calculate_rush_amount(
        cls,
        *,
        predefined_config: PredefinedSpecialOrderConfig,
        duration_days: int,
        running_total: Decimal,
    ) -> Decimal:
        """
        Calculate rush surcharge for short deadlines.
        """
        rule = (
            SpecialOrderRushSurchargeRule.objects.filter(
                website=predefined_config.website,
                predefined_order=predefined_config,
                max_duration_days__gte=duration_days,
                is_active=True,
            )
            .order_by("max_duration_days")
            .first()
        )

        if rule is None:
            return Decimal("0.00")

        return cls._percentage_amount(
            amount=running_total,
            percentage=rule.surcharge_percentage,
        )

    @classmethod
    def _calculate_writer_level_amount(
        cls,
        *,
        predefined_config: PredefinedSpecialOrderConfig,
        writer_level: str,
        running_total: Decimal,
    ) -> Decimal:
        """
        Calculate writer level surcharge.
        """
        if not writer_level:
            return Decimal("0.00")

        rule = (
            SpecialOrderWriterLevelSurchargeRule.objects.filter(
                website=predefined_config.website,
                predefined_order=predefined_config,
                writer_level=writer_level,
                is_active=True,
            )
            .order_by("-created_at")
            .first()
        )

        if rule is None:
            return Decimal("0.00")

        return cls._percentage_amount(
            amount=running_total,
            percentage=rule.surcharge_percentage,
        )

    @staticmethod
    def _validate_capacity(
        *,
        predefined_config: PredefinedSpecialOrderConfig,
        predefined_duration: PredefinedSpecialOrderDuration,
    ) -> None:
        """
        Validate active order capacity for this config/deadline.

        This is a placeholder-friendly rule. If your active statuses live
        elsewhere, move that list to constants.
        """
        rule = (
            SpecialOrderCapacityRule.objects.filter(
                website=predefined_config.website,
                predefined_order=predefined_config,
                duration_days=predefined_duration.duration_days,
                is_active=True,
            )
            .order_by("-created_at")
            .first()
        )

        if rule is None:
            return

        from special_orders.constants import SpecialOrderStatus
        from special_orders.models import SpecialOrder

        active_count = SpecialOrder.objects.filter(
            website=predefined_config.website,
            predefined_config=predefined_config,
            duration_days=predefined_duration.duration_days,
            status__in=[
                SpecialOrderStatus.AWAITING_PAYMENT,
                SpecialOrderStatus.PARTIALLY_FUNDED,
                SpecialOrderStatus.READY_FOR_STAFFING,
                SpecialOrderStatus.ASSIGNED,
                SpecialOrderStatus.IN_PROGRESS,
                SpecialOrderStatus.SUBMITTED,
                SpecialOrderStatus.READY_FOR_DELIVERY,
                SpecialOrderStatus.ON_REVISION,
            ],
        ).count()

        if active_count >= rule.max_active_orders:
            raise ValueError(
                "This predefined special order deadline is currently full."
            )

    @classmethod
    def _percentage_amount(
        cls,
        *,
        amount: Decimal,
        percentage: Decimal,
    ) -> Decimal:
        """
        Calculate percentage amount.
        """
        value = amount * (percentage / Decimal("100.00"))
        return cls._money(value)

    @staticmethod
    def _money(value: Decimal) -> Decimal:
        """
        Round money to two decimals.
        """
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)