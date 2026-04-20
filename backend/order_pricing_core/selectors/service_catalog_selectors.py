"""
Service catalog selectors for the order_pricing_core app.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError

from order_pricing_core.models import ServiceAddon
from order_pricing_core.models import ServiceCatalogItem


def get_service_catalog_item_by_id(
    *,
    website,
    item_id: int,
) -> ServiceCatalogItem:
    """
    Return a service catalog item by id for a website.
    """
    try:
        return ServiceCatalogItem.objects.get(
            id=item_id,
            website=website,
        )
    except ServiceCatalogItem.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Service catalog item not found."}
        ) from exc


def get_service_addon_by_id(
    *,
    website,
    item_id: int,
) -> ServiceAddon:
    """
    Return a service addon by id for a website.
    """
    try:
        return ServiceAddon.objects.get(
            id=item_id,
            website=website,
        )
    except ServiceAddon.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Service addon not found."}
        ) from exc