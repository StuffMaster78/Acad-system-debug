"""
Service to generate discount stacking hints for users.
"""

from discounts.services.config import DiscountConfigService


def get_discount_model():
    from discounts.models import Discount
    return Discount

class DiscountHintService:
    """
    Provides stackable discount hints based on current codes and website settings.
    """

    @staticmethod
    def get_stackable_hint(current_codes, website):
        """
        Return a stackable hint message if applicable.

        Args:
            current_codes (list): List of applied discount codes.
            website (Website): The website instance to fetch configuration.

        Returns:
            dict or None: Suggested discount code or None if no hint.
        """
        Discount = get_discount_model()
        config = DiscountConfigService.get_config(website)

        # If stacking or hints are disabled, return None
        if not config["ENABLE_HINTS"] or not config["ENABLE_STACKING"]:
            return None

        # If two or more codes are already applied, don't suggest more
        if len(current_codes) >= 2:
            return None

        # Fetch valid discounts based on current applied codes
        valid_discounts = Discount.objects.filter(
            code__in=current_codes,
            website=website,
            is_active=True
        )

        # If no valid discounts found, return None
        if not valid_discounts.exists():
            return None

        # Check for stackable discounts
        potential_discounts = Discount.objects.filter(
            is_active=True,
            stackable=True,
            website=website
        ).exclude(code__in=current_codes)

        for discount in potential_discounts:
            # Validate if the discount is stackable with the existing codes
            if all(d.stackable for d in valid_discounts):
                return {
                    "hint": f"You can stack this with another code: {discount.code}",
                    "suggested_code": discount.code
                }

        # If no suggestions found, return None
        return None