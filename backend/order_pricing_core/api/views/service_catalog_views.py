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
    DesignOrderServiceConfigSerializer,
)
from order_pricing_core.api.serializers.service_catalog_serializers import (
    DiagramOrderServiceConfigSerializer,
)
from order_pricing_core.api.serializers.service_catalog_serializers import (
    PaperOrderServiceConfigSerializer,
)
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


def _config_payload(item: ServiceCatalogItem) -> dict[str, Any]:
    """
    Return family-specific service config fields when present.
    """
    payload: dict[str, Any] = {}
    paper = getattr(item, "paper_order_config", None)
    if paper is not None:
        payload["paper_order_config"] = {
            "supports_pages": paper.uses_pages,
            "supports_spacing": paper.supports_spacing,
            "supports_academic_level": paper.supports_academic_level,
            "supports_paper_type": paper.supports_paper_type,
            "supports_work_type": paper.supports_work_type,
            "supports_subject": paper.supports_subject,
            "supports_analysis_level": paper.supports_analysis_level,
            "supports_writer_level": paper.supports_writer_level,
            "supports_preferred_writer": paper.supports_preferred_writer,
            "supports_deadline": paper.supports_deadline,
            "supports_files": paper.supports_files,
            "supports_topic": paper.supports_topic,
            "supports_instructions": paper.supports_instructions,
            "default_is_public": paper.default_is_public,
        }
    design = getattr(item, "design_order_config", None)
    if design is not None:
        payload["design_order_config"] = {
            "design_product_type": design.design_product_type,
            "default_package_type": design.default_package_type,
            "supports_quantity": design.supports_quantity,
            "supports_slides": design.supports_slides,
            "supports_deadline": design.supports_deadline,
            "supports_files": design.supports_files,
            "supports_topic": design.supports_topic,
            "supports_instructions": design.supports_instructions,
        }
    diagram = getattr(item, "diagram_order_config", None)
    if diagram is not None:
        payload["diagram_order_config"] = {
            "diagram_type": diagram.diagram_type,
            "supports_quantity": diagram.supports_quantity,
            "supports_complexity": diagram.supports_complexity,
            "supports_deadline": diagram.supports_deadline,
            "supports_files": diagram.supports_files,
            "supports_topic": diagram.supports_topic,
            "supports_instructions": diagram.supports_instructions,
        }
    return payload


def _item_payload(item: ServiceCatalogItem) -> dict[str, Any]:
    payload = {
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
    }
    payload.update(_config_payload(item))
    return payload


def _validated_config_data(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    configs: dict[str, dict[str, Any]] = {}
    config_specs = (
        ("paper_order_config", PaperOrderServiceConfigSerializer),
        ("design_order_config", DesignOrderServiceConfigSerializer),
        ("diagram_order_config", DiagramOrderServiceConfigSerializer),
    )
    for key, serializer_cls in config_specs:
        if key not in data:
            continue
        serializer = serializer_cls(data=data.pop(key), partial=True)
        serializer.is_valid(raise_exception=True)
        configs[key] = cast(dict[str, Any], serializer.validated_data)
    if "paper_order_config" in configs and "supports_pages" in configs["paper_order_config"]:
        configs["paper_order_config"]["uses_pages"] = configs["paper_order_config"].pop("supports_pages")
    return configs


class ServiceCatalogItemListCreateView(APIView):
    """
    List or create service catalog items.
    """

    permission_classes = [CanManagePricingConfig]

    def get(self, request: Request) -> Response:
        items = ServiceCatalogItem.objects.filter(
            website=request.website,
        ).order_by("sort_order", "id")

        return Response([_item_payload(item) for item in items], status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = ServiceCatalogItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)
        config_data = _validated_config_data(data)
        item = ServiceCatalogAdminService.create_service_catalog_item(
            website=request.website,
            data=data,
        )
        ServiceCatalogAdminService.update_service_family_config(
            item=item,
            paper_config=config_data.get("paper_order_config"),
            design_config=config_data.get("design_order_config"),
            diagram_config=config_data.get("diagram_order_config"),
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

        return Response(_item_payload(item), status=status.HTTP_200_OK)

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
        config_data = _validated_config_data(data)

        for field, value in data.items():
            setattr(item, field, value)

        validate_service_catalog_item(item)
        item.save()
        ServiceCatalogAdminService.update_service_family_config(
            item=item,
            paper_config=config_data.get("paper_order_config"),
            design_config=config_data.get("design_order_config"),
            diagram_config=config_data.get("diagram_order_config"),
        )

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

class PublicServiceAddonListView(APIView):
    """
    GET /pricing/public/addons/?service_code=<code>&website_id=<id>
    Public read-only endpoint — returns active, public addons for a website.
    Used by the order creation form to show available add-ons.
    """
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        from websites.models.websites import Website

        website = getattr(request, "website", None)
        website_id = request.query_params.get("website_id")
        if website_id and not website:
            try:
                website = Website.objects.get(pk=website_id)
            except Website.DoesNotExist:
                pass

        if not website:
            return Response([])

        qs = ServiceAddon.objects.filter(
            website=website,
            is_active=True,
            is_public=True,
        ).order_by("sort_order")

        service_code = request.query_params.get("service_code")
        if service_code:
            from order_pricing_core.models.service_catalog import ServiceAddonApplicability
            addon_ids = ServiceAddonApplicability.objects.filter(
                addon__website=website,
                service__service_code=service_code,
            ).values_list("addon_id", flat=True)
            qs = qs.filter(id__in=addon_ids)

        return Response([
            {
                "id":          a.id,
                "addon_code":  a.addon_code,
                "name":        a.name,
                "description": a.description,
                "flat_amount": str(a.flat_amount),
            }
            for a in qs
        ])
