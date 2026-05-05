from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from discounts.constants import PayableType
from discounts.exceptions import DiscountValidationError
from discounts.models.discount import Discount
from discounts.selectors.discount_selectors import DiscountSelector
from discounts.selectors.discount_settings_selectors import (
    DiscountSettingsSelector,
)
from discounts.services.discount_calculation_service import (
    DiscountCalculationService,
)
from discounts.services.discount_validation_service import (
    DiscountValidationService,
)
from discounts.services.first_order_discount_policy import (
    FirstOrderDiscountPolicy,
)


@dataclass(frozen=True)
class ResolvedDiscount:
    """
    Final discount selected for a payable object.
    """

    discount: Discount
    discount_code: str
    discount_type: str
    discount_value: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    origin: str
    source: str


class DiscountResolutionService:
    """
    Resolve the single best discount for a payable object.
    """

    @classmethod
    def resolve(
        cls,
        *,
        website,
        client,
        subtotal: Decimal,
        payable_type: str,
        has_prior_paid_purchase: bool,
        entered_code: str | None = None,
        lifetime_spend: Decimal | None = None,
    ) -> ResolvedDiscount | None:
        """
        Return the best valid discount for the client.
        """
        lifetime_spend = lifetime_spend or Decimal("0.00")

        settings = DiscountSettingsSelector.get_or_create_for_website(
            website=website,
        )

        cls._validate_payable_allowed(
            settings=settings,
            payable_type=payable_type,
        )

        candidates: list[ResolvedDiscount] = []

        first_order_discount = cls._resolve_first_order_discount(
            settings=settings,
            website=website,
            client=client,
            subtotal=subtotal,
            payable_type=payable_type,
            has_prior_paid_purchase=has_prior_paid_purchase,
            lifetime_spend=lifetime_spend,
        )

        if first_order_discount is not None:
            candidates.append(first_order_discount)

        entered_discount = cls._resolve_entered_code(
            settings=settings,
            website=website,
            client=client,
            subtotal=subtotal,
            entered_code=entered_code,
            lifetime_spend=lifetime_spend,
        )

        if entered_discount is not None:
            candidates.append(entered_discount)

        if not candidates:
            return None

        if not settings.auto_apply_best_discount:
            return cls._pick_by_priority(candidates=candidates)

        return cls._pick_best_candidate(candidates=candidates)

    @classmethod
    def _resolve_first_order_discount(
        cls,
        *,
        settings,
        website,
        client,
        subtotal: Decimal,
        payable_type: str,
        has_prior_paid_purchase: bool,
        lifetime_spend: Decimal,
    ) -> ResolvedDiscount | None:
        """
        Resolve automatic first order discount if enabled.
        """
        if not settings.auto_apply_first_order_discount:
            return None

        discount = FirstOrderDiscountPolicy.get_discount(
            website=website,
            payable_type=payable_type,
            has_prior_paid_purchase=has_prior_paid_purchase,
        )

        if discount is None:
            return None

        DiscountValidationService.validate_for_client(
            discount=discount,
            website=website,
            client=client,
            subtotal=subtotal,
            lifetime_spend=lifetime_spend,
        )

        return cls._build_resolved_candidate(
            discount=discount,
            subtotal=subtotal,
            source="first_order",
        )

    @classmethod
    def _resolve_entered_code(
        cls,
        *,
        settings,
        website,
        client,
        subtotal: Decimal,
        entered_code: str | None,
        lifetime_spend: Decimal,
    ) -> ResolvedDiscount | None:
        """
        Resolve a manually entered code if allowed.
        """
        if not entered_code:
            return None

        if not settings.allow_manual_codes:
            raise DiscountValidationError(
                "Manual discount codes are not allowed."
            )

        discount = DiscountSelector.get_by_code(
            website=website,
            code=entered_code,
        )

        if discount is None:
            raise DiscountValidationError("Invalid discount code.")

        DiscountValidationService.validate_for_client(
            discount=discount,
            website=website,
            client=client,
            subtotal=subtotal,
            lifetime_spend=lifetime_spend,
        )

        return cls._build_resolved_candidate(
            discount=discount,
            subtotal=subtotal,
            source="entered_code",
        )

    @staticmethod
    def _validate_payable_allowed(*, settings, payable_type: str) -> None:
        """
        Ensure discounts are enabled for the payable type.
        """
        if (
            payable_type == PayableType.ORDER
            and not settings.allow_discounts_on_orders
        ):
            raise DiscountValidationError(
                "Discounts are not enabled for orders."
            )

        if (
            payable_type == PayableType.SPECIAL_ORDER
            and not settings.allow_discounts_on_special_orders
        ):
            raise DiscountValidationError(
                "Discounts are not enabled for special orders."
            )

        if (
            payable_type == PayableType.CLASS_ORDER
            and not settings.allow_discounts_on_class_bundles
        ):
            raise DiscountValidationError(
                "Discounts are not enabled for class bundles."
            )

    @classmethod
    def _build_resolved_candidate(
        cls,
        *,
        discount: Discount,
        subtotal: Decimal,
        source: str,
    ) -> ResolvedDiscount:
        """
        Convert a discount into a resolved result.
        """
        discount_amount = DiscountCalculationService.calculate_amount(
            discount=discount,
            subtotal=subtotal,
        )
        final_amount = DiscountCalculationService.calculate_final_amount(
            discount=discount,
            subtotal=subtotal,
        )

        return ResolvedDiscount(
            discount=discount,
            discount_code=discount.discount_code,
            discount_type=discount.discount_type,
            discount_value=discount.discount_value,
            discount_amount=discount_amount,
            final_amount=final_amount,
            origin=discount.origin,
            source=source,
        )

    @staticmethod
    def _pick_best_candidate(
        *,
        candidates: list[ResolvedDiscount],
    ) -> ResolvedDiscount:
        """
        Pick highest value. On tie, prefer entered code.
        """
        return max(
            candidates,
            key=lambda item: (
                item.discount_amount,
                item.source == "entered_code",
            ),
        )

    @staticmethod
    def _pick_by_priority(
        *,
        candidates: list[ResolvedDiscount],
    ) -> ResolvedDiscount:
        """
        Pick first order first unless user code is the only option.
        """
        for candidate in candidates:
            if candidate.source == "first_order":
                return candidate

        return candidates[0]