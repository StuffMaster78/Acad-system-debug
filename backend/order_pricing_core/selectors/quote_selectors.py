"""
Quote selectors for the order_pricing_core app.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError

from order_pricing_core.models import PricingQuote


def get_quote_by_session_id(*, session_id) -> PricingQuote:
    """
    Return a quote by session id.
    """
    try:
        return PricingQuote.objects.get(session_id=session_id)
    except PricingQuote.DoesNotExist as exc:
        raise ValidationError(
            {"session_id": "Quote not found."}
        ) from exc