from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from django.db.models import Count

from discounts.constants import DiscountOrigin
from discounts.exceptions import DiscountValidationError
from discounts.models.discount import Discount
from discounts.models.discount_usage import DiscountUsage
from discounts.selectors.discount_selectors import DiscountSelector
from discounts.services.discount_calculation_service import (
    DiscountCalculationService,
)
from discounts.services.discount_tier_service import DiscountTierService
from discounts.services.discount_validation_service import (
    DiscountValidationService,
)


@dataclass(frozen=True)
class AvailableDiscount:
    """
    Client-facing available discount option.
    """

    discount_id: int
    discount_code: str
    name: str
    description: str
    origin: str
    discount_type: str
    discount_value: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    usage_remaining: int | None
    client_usage_remaining: int | None
    expires_at: datetime | None
    reason: str
    explanation: str
    frontend_label: str
    frontend_badge: str
    cta_label: str


class AvailableDiscountService:
    """
    Build selectable discount options for clients.
    """

    @staticmethod
    def list_available_for_client(
        *,
        website,
        client,
        subtotal: Decimal,
        lifetime_spend: Decimal | None = None,
    ) -> list[AvailableDiscount]:
        """
        Return usable discount options for a client.

        Usage counts are loaded in bulk to avoid N+1 queries while
        building frontend-ready discount cards.
        """
        lifetime_spend = lifetime_spend or Decimal("0.00")

        standard_discounts = list(
            DiscountSelector.list_working(website=website)
        )
        tier_discounts = DiscountTierService.get_eligible_discounts(
            website=website,
            lifetime_spend=lifetime_spend,
        )

        discounts = AvailableDiscountService._dedupe_discounts(
            discounts=standard_discounts + tier_discounts,
        )
        discount_ids = [discount.pk for discount in discounts]

        total_usage_map = AvailableDiscountService._get_total_usage_map(
            website=website,
            discount_ids=discount_ids,
        )
        client_usage_map = AvailableDiscountService._get_client_usage_map(
            website=website,
            client=client,
            discount_ids=discount_ids,
        )

        available: list[AvailableDiscount] = []

        for discount in discounts:
            try:
                DiscountValidationService.validate_for_client(
                    discount=discount,
                    website=website,
                    client=client,
                    subtotal=subtotal,
                    lifetime_spend=lifetime_spend,
                )
            except DiscountValidationError:
                continue

            discount_amount = (
                DiscountCalculationService.calculate_amount(
                    discount=discount,
                    subtotal=subtotal,
                )
            )
            final_amount = (
                DiscountCalculationService.calculate_final_amount(
                    discount=discount,
                    subtotal=subtotal,
                )
            )

            total_used = total_usage_map.get(discount.pk, 0)
            client_used = client_usage_map.get(discount.pk, 0)

            available.append(
                AvailableDiscount(
                    discount_id=discount.pk,
                    discount_code=discount.discount_code,
                    name=discount.name,
                    description=discount.description,
                    origin=discount.origin,
                    discount_type=discount.discount_type,
                    discount_value=discount.discount_value,
                    discount_amount=discount_amount,
                    final_amount=final_amount,
                    usage_remaining=(
                        AvailableDiscountService._get_usage_remaining(
                            discount=discount,
                            used_count=total_used,
                        )
                    ),
                    client_usage_remaining=(
                        AvailableDiscountService
                        ._get_client_usage_remaining(
                            discount=discount,
                            used_count=client_used,
                        )
                    ),
                    expires_at=discount.ends_at,
                    reason="You are eligible for this discount.",
                    explanation=(
                        AvailableDiscountService._get_explanation(
                            discount=discount,
                            lifetime_spend=lifetime_spend,
                        )
                    ),
                    frontend_label=(
                        AvailableDiscountService._get_frontend_label(
                            discount=discount,
                        )
                    ),
                    frontend_badge=(
                        AvailableDiscountService._get_frontend_badge(
                            discount=discount,
                        )
                    ),
                    cta_label=f"Use {discount.discount_code}",
                )
            )

        return sorted(
            available,
            key=lambda item: item.discount_amount,
            reverse=True,
        )

    @staticmethod
    def _dedupe_discounts(
        *,
        discounts: Iterable[Discount],
    ) -> list[Discount]:
        """
        De-duplicate discount objects by ID.
        """
        seen: set[int] = set()
        unique: list[Discount] = []

        for discount in discounts:
            if discount.pk in seen:
                continue

            seen.add(discount.pk)
            unique.append(discount)

        return unique

    @staticmethod
    def _get_total_usage_map(
        *,
        website,
        discount_ids: list[int],
    ) -> dict[int, int]:
        """
        Return total usage counts keyed by discount ID.
        """
        if not discount_ids:
            return {}

        rows = (
            DiscountUsage.objects.filter(
                website=website,
                discount_id__in=discount_ids,
            )
            .values("discount_id")
            .annotate(count=Count("id"))
        )

        return {
            row["discount_id"]: row["count"]
            for row in rows
        }

    @staticmethod
    def _get_client_usage_map(
        *,
        website,
        client,
        discount_ids: list[int],
    ) -> dict[int, int]:
        """
        Return client usage counts keyed by discount ID.
        """
        if not discount_ids:
            return {}

        rows = (
            DiscountUsage.objects.filter(
                website=website,
                client=client,
                discount_id__in=discount_ids,
            )
            .values("discount_id")
            .annotate(count=Count("id"))
        )

        return {
            row["discount_id"]: row["count"]
            for row in rows
        }

    @staticmethod
    def _get_usage_remaining(
        *,
        discount: Discount,
        used_count: int,
    ) -> int | None:
        """
        Return global usage remaining for a discount.
        """
        if discount.usage_limit is None:
            return None

        return max(discount.usage_limit - used_count, 0)

    @staticmethod
    def _get_client_usage_remaining(
        *,
        discount: Discount,
        used_count: int,
    ) -> int | None:
        """
        Return client usage remaining for a discount.
        """
        if discount.per_client_usage_limit is None:
            return None

        return max(discount.per_client_usage_limit - used_count, 0)

    @staticmethod
    def _get_explanation(
        *,
        discount: Discount,
        lifetime_spend: Decimal,
    ) -> str:
        """
        Return a human-friendly eligibility explanation.
        """

        if discount.origin == DiscountOrigin.SPEND_TIER:
            tier = getattr(discount, "spend_tier", None)

            if tier is None:
                return "You qualify for this spend tier reward."

        if discount.origin == DiscountOrigin.HOLIDAY:
            return "This is a limited-time holiday offer."

        if discount.origin == DiscountOrigin.LOYALTY:
            return "This discount was created from your loyalty rewards."

        if discount.origin == DiscountOrigin.FIRST_ORDER:
            return "This is your automatic first order discount."

        return "You qualify for this discount."

    @staticmethod
    def _get_frontend_label(*, discount: Discount) -> str:
        """
        Return a display label for the frontend.
        """
        if discount.origin == DiscountOrigin.SPEND_TIER:
            return "Tier reward"

        if discount.origin == DiscountOrigin.HOLIDAY:
            return "Holiday offer"

        if discount.origin == DiscountOrigin.LOYALTY:
            return "Loyalty reward"

        if discount.origin == DiscountOrigin.FIRST_ORDER:
            return "First order offer"

        return "Discount"

    @staticmethod
    def _get_frontend_badge(*, discount: Discount) -> str:
        """
        Return a badge label for the frontend.
        """
        if discount.origin == DiscountOrigin.SPEND_TIER:
            return "You qualify"

        if discount.origin == DiscountOrigin.HOLIDAY:
            return "Limited time"

        if discount.origin == DiscountOrigin.LOYALTY:
            return "Reward"

        if discount.origin == DiscountOrigin.FIRST_ORDER:
            return "Auto applied"

        return "Available"