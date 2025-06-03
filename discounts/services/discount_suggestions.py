"""
Service to generate discount suggestions for users or anonymous visitors.
Supports caching, personalization, and hint generation for discounts.
"""

import logging
from typing import List, Optional

from django.core.cache import cache
from django.utils.timezone import now

from discounts.models import Discount

logger = logging.getLogger(__name__)


class DiscountSuggestionService:
    """
    Provides top discount suggestions for a given website and user context.
    """

    @staticmethod
    def get_suggestions(
        website,
        client_email: Optional[str] = None,
        limit: int = 3,
        cache_timeout: int = 300
    ) -> List[dict]:
        """
        Retrieve top discount suggestions for a website or specific user.

        Args:
            website: Website instance the discounts belong to.
            client_email (str, optional): If provided, filter personalized 
                discounts for the email.
            limit (int): Max number of discounts to return (default: 3).
            cache_timeout (int): Cache duration in seconds (default: 300).

        Returns:
            List[dict]: List of suggested discounts with hints and metadata.
        """
        cache_key = (
            f"discount_suggestions:{website.id}:{client_email or 'anon'}:{limit}"
        )

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        current_time = now()

        discounts_qs = Discount.objects.filter(
            website=website,
            is_active=True,
            valid_from__lte=current_time,
            valid_until__gte=current_time
        )

        if client_email:
            discounts_qs = discounts_qs.filter(
                assigned_email__in=["", client_email]
            )

        discounts_qs = discounts_qs.order_by(
            "-usage_count", "-created_at"
        )

        discounts = discounts_qs[:limit]

        if not discounts.exists():
            logger.info(
                f"No active discount suggestions for website {website.id}"
            )
            return []

        suggestions = []
        for discount in discounts:
            hint = DiscountSuggestionService._generate_hint(discount)
            suggestions.append({
                "code": discount.code,
                "description": discount.description,
                "percentage": discount.percentage,
                "flat_amount": discount.flat_amount,
                "stackable": discount.stackable,
                "seasonal_event": (
                    discount.seasonal_event.name
                    if discount.seasonal_event else None
                ),
                "hint": hint
            })

        cache.set(cache_key, suggestions, timeout=cache_timeout)
        return suggestions

    @staticmethod
    def _generate_hint(discount: Discount) -> str:
        """
        Generate a hint message for a given discount.

        Args:
            discount (Discount): Discount instance.

        Returns:
            str: Contextual hint message for the discount.
        """
        if discount.seasonal_event:
            return f"🎉 Limited time for {discount.seasonal_event.name}!"
        if discount.percentage:
            return f"Save {discount.percentage}% now!"
        if discount.flat_amount:
            return f"Save ${discount.flat_amount} instantly!"
        return "Use this discount before it expires!"