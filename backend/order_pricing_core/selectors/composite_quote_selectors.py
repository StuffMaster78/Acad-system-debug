"""
Composite quote selectors for the order_pricing_core app.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError

from order_pricing_core.models import CompositePricingQuote


def get_composite_quote_by_session_id(
    *,
    session_id,
) -> CompositePricingQuote:
    """
    Return a composite quote by session id.
    """
    try:
        return CompositePricingQuote.objects.get(
            session_id=session_id,
        )
    except CompositePricingQuote.DoesNotExist as exc:
        raise ValidationError(
            {"session_id": "Composite quote not found."}
        ) from exc