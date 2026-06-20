from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.utils import timezone


class DeadlineDecreasePricingService:
    """
    Compute the client surcharge for requesting a sooner deadline.

    Rush pricing uses the site's DeadlineRate bands (same bands used at
    order creation). The surcharge is the price delta between the new
    and original deadline bands applied to the current order total.
    """

    @staticmethod
    def get_rate_for_hours(hours: float, website: Any) -> Decimal:
        """Return the multiplier for a deadline that is `hours` away."""
        from order_pricing_core.models.pricing_dimensions import DeadlineRate
        rate = (
            DeadlineRate.objects
            .filter(website=website, max_hours__gte=int(hours), is_active=True)
            .order_by("max_hours", "sort_order")
            .first()
        )
        return rate.multiplier if rate else Decimal("1.0000")

    @staticmethod
    def compute_surcharge(*, order: Any, new_deadline: Any) -> dict:
        """
        Returns:
            {
                client_surcharge: Decimal   — additional amount client must pay
                writer_comp_delta: Decimal  — additional writer earnings (currently 0,
                                             staff can override via adjustment)
                new_multiplier: Decimal     — DeadlineRate multiplier for new deadline
                original_multiplier: Decimal — DeadlineRate multiplier for current deadline
                new_hours: float
                original_hours: float
            }
        """
        now = timezone.now()

        new_hours = max(0.0, (new_deadline - now).total_seconds() / 3600)
        original_deadline = getattr(order, "client_deadline", None)
        original_hours = (
            max(0.0, (original_deadline - now).total_seconds() / 3600)
            if original_deadline else 9999.0
        )

        website = order.website
        new_mult = DeadlineDecreasePricingService.get_rate_for_hours(new_hours, website)
        orig_mult = DeadlineDecreasePricingService.get_rate_for_hours(original_hours, website)

        # Surcharge only when moving into a more expensive band
        if new_mult <= orig_mult or orig_mult <= 0:
            surcharge = Decimal("0.00")
        else:
            # Estimate base price by reversing the original multiplier
            total = Decimal(str(getattr(order, "total_price", "0.00") or "0.00"))
            base = (total / orig_mult).quantize(Decimal("0.01"))
            surcharge = (base * (new_mult - orig_mult)).quantize(Decimal("0.01"))

        return {
            "client_surcharge": surcharge,
            "writer_comp_delta": Decimal("0.00"),
            "new_multiplier": new_mult,
            "original_multiplier": orig_mult,
            "new_hours": round(new_hours, 1),
            "original_hours": round(original_hours, 1),
        }
