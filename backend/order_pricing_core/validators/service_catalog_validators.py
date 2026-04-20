"""
Service catalog validators for the order_pricing_core app.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError

from order_pricing_core.models import ServiceCatalogItem


def validate_service_catalog_item(
    item: ServiceCatalogItem,
) -> None:
    """
    Validate service catalog item values.
    """
    if item.base_amount < Decimal("0.00"):
        raise ValidationError(
            {"base_amount": "Base amount cannot be negative."}
        )

    if item.minimum_charge < Decimal("0.00"):
        raise ValidationError(
            {"minimum_charge": "Minimum charge cannot be negative."}
        )