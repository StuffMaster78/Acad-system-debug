"""
Admin service for service catalog management.
"""

from __future__ import annotations

from django.db import transaction

from order_pricing_core.models import ServiceAddon
from order_pricing_core.models import ServiceCatalogItem
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_non_negative_amount,
)
from order_pricing_core.validators.service_catalog_validators import (
    validate_service_catalog_item,
)


class ServiceCatalogAdminService:
    """
    Admin-facing service for service catalog and addon management.
    """

    @classmethod
    @transaction.atomic
    def create_service_catalog_item(
        cls,
        *,
        website,
        data: dict,
    ) -> ServiceCatalogItem:
        """
        Create a service catalog item.
        """
        item = ServiceCatalogItem(
            website=website,
            **data,
        )
        validate_service_catalog_item(item)
        item.save()
        return item

    @classmethod
    @transaction.atomic
    def create_service_addon(
        cls,
        *,
        website,
        data: dict,
    ) -> ServiceAddon:
        """
        Create a service addon.
        """
        validate_non_negative_amount(
            amount=data["flat_amount"],
            field_name="flat_amount",
        )
        return ServiceAddon.objects.create(
            website=website,
            **data,
        )