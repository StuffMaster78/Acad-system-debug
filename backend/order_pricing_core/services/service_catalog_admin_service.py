"""
Admin service for service catalog management.
"""

from __future__ import annotations

from django.db import transaction

from order_pricing_core.models import ServiceAddon
from order_pricing_core.models import ServiceCatalogItem
from order_pricing_core.models.service_catalog import DesignOrderServiceConfig
from order_pricing_core.models.service_catalog import DiagramOrderServiceConfig
from order_pricing_core.models.service_catalog import PaperOrderServiceConfig
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
        paper_config = data.pop("paper_order_config", None)
        design_config = data.pop("design_order_config", None)
        diagram_config = data.pop("diagram_order_config", None)
        item = ServiceCatalogItem(
            website=website,
            **data,
        )
        validate_service_catalog_item(item)
        item.save()
        cls.update_service_family_config(
            item=item,
            paper_config=paper_config,
            design_config=design_config,
            diagram_config=diagram_config,
        )
        return item

    @classmethod
    @transaction.atomic
    def update_service_family_config(
        cls,
        *,
        item: ServiceCatalogItem,
        paper_config: dict | None = None,
        design_config: dict | None = None,
        diagram_config: dict | None = None,
    ) -> None:
        """
        Create or update the family-specific config for a catalog item.
        """
        if paper_config is not None:
            PaperOrderServiceConfig.objects.update_or_create(
                service=item,
                defaults=paper_config,
            )
        if design_config is not None:
            DesignOrderServiceConfig.objects.update_or_create(
                service=item,
                defaults=design_config,
            )
        if diagram_config is not None:
            DiagramOrderServiceConfig.objects.update_or_create(
                service=item,
                defaults=diagram_config,
            )

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
