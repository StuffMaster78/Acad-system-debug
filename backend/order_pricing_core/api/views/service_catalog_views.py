"""
Admin-facing service catalog API views.
"""

from __future__ import annotations

from typing import Any
from typing import cast

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from order_pricing_core.api.serializers.service_catalog_serializers import (
    ServiceAddonSerializer,
)
from order_pricing_core.api.serializers.service_catalog_serializers import (
    ServiceCatalogItemSerializer,
)
from order_pricing_core.models import ServiceAddon
from order_pricing_core.models import ServiceCatalogItem
from order_pricing_core.permissions import CanManagePricingConfig
from order_pricing_core.selectors.service_catalog_selectors import (
    get_service_addon_by_id,
)
from order_pricing_core.selectors.service_catalog_selectors import (
    get_service_catalog_item_by_id,
)
from order_pricing_core.services.service_catalog_admin_service import (
    ServiceCatalogAdminService,
)
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_non_negative_amount,
)
from order_pricing_core.validators.service_catalog_validators import (
    validate_service_catalog_item,
)


class ServiceCatalogItemListCreateView(APIView):
    """
    List or create service catalog items.
    """

    permission_classes = [CanManagePricingConfig]

    def get(self, request: Request) -> Response:
        items = ServiceCatalogItem.objects.filter(
            website=request.website,
        ).order_by("sort_order", "id")

        return Response(
            [
                {
                    "id": item.pk,
                    "service_code": item.service_code,
                    "name": item.name,
                    "service_family": item.service_family,
                    "pricing_strategy": item.pricing_strategy,
                    "pricing_unit": item.pricing_unit,
                    "base_amount": item.base_amount,
                    "minimum_charge": item.minimum_charge,
                    "is_public": item.is_public,
                    "is_active": item.is_active,
                    "sort_order": item.sort_order,
                }
                for item in items
            ],
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = ServiceCatalogItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)
        item = ServiceCatalogAdminService.create_service_catalog_item(
            website=request.website,
            data=data,
        )

        return Response(
            {
                "id": item.pk,
                "service_code": item.service_code,
                "name": item.name,
            },
            status=status.HTTP_201_CREATED,
        )


class ServiceCatalogItemDetailView(APIView):
    """
    Retrieve, update, or delete a service catalog item.
    """

    permission_classes = [CanManagePricingConfig]

    def get(self, request: Request, item_id: int) -> Response:
        item = get_service_catalog_item_by_id(
            website=request.website,
            item_id=item_id,
        )

        return Response(
            {
                "id": item.pk,
                "service_code": item.service_code,
                "name": item.name,
                "description": item.description,
                "service_family": item.service_family,
                "pricing_strategy": item.pricing_strategy,
                "pricing_unit": item.pricing_unit,
                "base_amount": item.base_amount,
                "minimum_charge": item.minimum_charge,
                "is_public": item.is_public,
                "is_active": item.is_active,
                "sort_order": item.sort_order,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request: Request, item_id: int) -> Response:
        item = get_service_catalog_item_by_id(
            website=request.website,
            item_id=item_id,
        )

        serializer = ServiceCatalogItemSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        for field, value in data.items():
            setattr(item, field, value)

        validate_service_catalog_item(item)
        item.save()

        return Response(
            {
                "id": item.pk,
                "service_code": item.service_code,
                "name": item.name,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, item_id: int) -> Response:
        item = get_service_catalog_item_by_id(
            website=request.website,
            item_id=item_id,
        )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ServiceAddonListCreateView(APIView):
    """
    List or create service addons.
    """

    permission_classes = [CanManagePricingConfig]

    def get(self, request: Request) -> Response:
        addons = ServiceAddon.objects.filter(
            website=request.website,
        ).order_by("sort_order", "id")

        return Response(
            [
                {
                    "id": addon.pk,
                    "addon_code": addon.addon_code,
                    "name": addon.name,
                    "description": addon.description,
                    "flat_amount": addon.flat_amount,
                    "is_public": addon.is_public,
                    "is_active": addon.is_active,
                    "sort_order": addon.sort_order,
                }
                for addon in addons
            ],
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = ServiceAddonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)
        addon = ServiceCatalogAdminService.create_service_addon(
            website=request.website,
            data=data,
        )

        return Response(
            {
                "id": addon.pk,
                "addon_code": addon.addon_code,
                "name": addon.name,
            },
            status=status.HTTP_201_CREATED,
        )


class ServiceAddonDetailView(APIView):
    """
    Retrieve, update, or delete a service addon.
    """

    permission_classes = [CanManagePricingConfig]

    def get(self, request: Request, item_id: int) -> Response:
        addon = get_service_addon_by_id(
            website=request.website,
            item_id=item_id,
        )

        return Response(
            {
                "id": addon.pk,
                "addon_code": addon.addon_code,
                "name": addon.name,
                "description": addon.description,
                "flat_amount": addon.flat_amount,
                "is_public": addon.is_public,
                "is_active": addon.is_active,
                "sort_order": addon.sort_order,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request: Request, item_id: int) -> Response:
        addon = get_service_addon_by_id(
            website=request.website,
            item_id=item_id,
        )

        serializer = ServiceAddonSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        if "flat_amount" in data:
            validate_non_negative_amount(
                amount=data["flat_amount"],
                field_name="flat_amount",
            )

        for field, value in data.items():
            setattr(addon, field, value)

        addon.save()

        return Response(
            {
                "id": addon.pk,
                "addon_code": addon.addon_code,
                "name": addon.name,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, item_id: int) -> Response:
        addon = get_service_addon_by_id(
            website=request.website,
            item_id=item_id,
        )
        addon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)