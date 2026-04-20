"""
Composite quote validators for the order_pricing_core app.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError

from order_pricing_core.models import PricingQuote


def validate_component_quotes(
    *,
    website,
    quotes: list[PricingQuote],
) -> None:
    """
    Validate component quotes for composite pricing.
    """
    if not quotes:
        raise ValidationError(
            {"component_quotes": "At least one quote is required."}
        )

    seen_ids: set[int] = set()

    for quote in quotes:
        if quote.pk is None:
            raise ValidationError(
                {
                    "component_quotes": (
                        "Each component quote must be saved before it "
                        "can be used in a composite quote."
                    )
                }
            )

        if quote.pk in seen_ids:
            raise ValidationError(
                {
                    "component_quotes": (
                        "Duplicate component quote found."
                    )
                }
            )
        seen_ids.add(quote.pk)

        if quote.website.pk != website.pk:
            raise ValidationError(
                {
                    "component_quotes": (
                        "All component quotes must belong to the same "
                        "website."
                    )
                }
            )

        if quote.calculated_price is None:
            raise ValidationError(
                {
                    "component_quotes": (
                        "Each component quote must have a calculated "
                        "price."
                    )
                }
            )

        if quote.calculated_price < Decimal("0.00"):
            raise ValidationError(
                {
                    "component_quotes": (
                        "Component quote price cannot be negative."
                    )
                }
            )


def validate_composite_not_final(is_final: bool) -> None:
    """
    Ensure a composite quote is still mutable.
    """
    if is_final:
        raise ValidationError(
            {
                "composite_quote": (
                    "Finalized composite quote cannot change."
                )
            }
        )