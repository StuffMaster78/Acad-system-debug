"""
Public, non-persistent pricing estimates for marketing calculators.
"""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from order_pricing_core.calculators.paper_order_calculator import (
    PaperOrderPricingCalculator,
)
from order_pricing_core.constants import QuoteMode
from order_pricing_core.constants import ServiceFamily
from order_pricing_core.constants import SpacingMode
from order_pricing_core.models import AcademicLevelRate
from order_pricing_core.models import PaperTypeRate
from order_pricing_core.models import ServiceCatalogItem
from order_pricing_core.models import SubjectRate
from order_pricing_core.models import WebsitePricingProfile
from order_pricing_core.models import WorkTypeRate
from websites.models.websites import Website


class PublicPaperEstimateSerializer(serializers.Serializer):
    """Small public calculator payload."""

    service_code = serializers.CharField(required=False, allow_blank=True)
    pages = serializers.IntegerField(min_value=1, max_value=500)
    deadline_hours = serializers.IntegerField(min_value=1)
    spacing = serializers.ChoiceField(
        choices=SpacingMode.CHOICES,
        default=SpacingMode.DEFAULT,
    )
    paper_type_code = serializers.CharField(required=False, allow_blank=True)
    work_type_code = serializers.CharField(required=False, allow_blank=True)
    subject_code = serializers.CharField(required=False, allow_blank=True)
    academic_level_code = serializers.CharField(
        required=False,
        allow_blank=True,
    )


def _resolve_website(request) -> Website | None:
    website = getattr(request, "website", None)
    if website is not None:
        return website

    website_id = request.query_params.get("website_id")
    if website_id:
        return Website.objects.filter(
            pk=website_id,
            is_active=True,
            is_deleted=False,
        ).first()

    gradecrest = Website.objects.filter(
        is_active=True,
        is_deleted=False,
        domain__icontains="gradecrest",
    ).first()
    if gradecrest is not None:
        return gradecrest

    return Website.objects.filter(is_active=True, is_deleted=False).first()


def _active_code(model, *, website, requested: str) -> str:
    queryset = model.objects.filter(website=website, is_active=True)
    if requested and queryset.filter(code=requested).exists():
        return requested

    item = queryset.order_by("sort_order", "id").first()
    if item is None:
        raise DjangoValidationError(
            {model.__name__: "No active pricing option is configured."}
        )
    return item.code


def _service_for(*, website, requested: str) -> ServiceCatalogItem:
    queryset = ServiceCatalogItem.objects.filter(
        website=website,
        service_family=ServiceFamily.PAPER_ORDER,
        is_active=True,
        is_public=True,
    )
    if requested:
        service = queryset.filter(service_code=requested).first()
        if service is not None:
            return service

    service = queryset.order_by("sort_order", "id").first()
    if service is None:
        raise DjangoValidationError(
            {"service_code": "No public paper service is configured."}
        )
    return service


def _money(value) -> str | None:
    return str(value) if value is not None else None


class PublicPaperEstimateView(APIView):
    """
    POST /api/v1/pricing/public/estimate/

    Returns a backend-derived price for public marketing calculators without
    creating a quote session or pricing snapshot.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request) -> Response:
        serializer = PublicPaperEstimateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data: dict[str, Any] = dict(serializer.validated_data)

        website = _resolve_website(request)
        if website is None:
            return Response(
                {"detail": "No website is available for pricing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = _service_for(
                website=website,
                requested=data.get("service_code", ""),
            )
            payload = {
                **data,
                "service_code": service.service_code,
                "paper_type_code": _active_code(
                    PaperTypeRate,
                    website=website,
                    requested=data.get("paper_type_code", ""),
                ),
                "work_type_code": _active_code(
                    WorkTypeRate,
                    website=website,
                    requested=data.get("work_type_code", ""),
                ),
                "subject_code": _active_code(
                    SubjectRate,
                    website=website,
                    requested=data.get("subject_code", ""),
                ),
                "academic_level_code": _active_code(
                    AcademicLevelRate,
                    website=website,
                    requested=data.get("academic_level_code", ""),
                ),
                "selected_addon_codes": [],
            }
            result = PaperOrderPricingCalculator().calculate(
                website=website,
                service=service,
                payload=payload,
                mode=QuoteMode.FINAL,
            )
            estimate_source = "configured"
        except (DjangoValidationError, ObjectDoesNotExist):
            try:
                service = _service_for(
                    website=website,
                    requested=data.get("service_code", ""),
                )
                result = PaperOrderPricingCalculator().calculate(
                    website=website,
                    service=service,
                    payload={
                        **data,
                        "service_code": service.service_code,
                    },
                    mode=QuoteMode.ESTIMATE,
                )
                estimate_source = "range"
            except (DjangoValidationError, ObjectDoesNotExist):
                return Response(
                    {
                        "detail": (
                            "Pricing is not fully configured for this website."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        profile = WebsitePricingProfile.objects.filter(
            website=website,
            is_active=True,
        ).first()

        return Response(
            {
                "currency": profile.currency if profile else "USD",
                "source": estimate_source,
                "total": _money(result.total),
                "estimated_min_price": result.metadata.get(
                    "estimated_min_price",
                    _money(result.total),
                ),
                "estimated_max_price": result.metadata.get(
                    "estimated_max_price",
                    _money(result.total),
                ),
                "metadata": result.metadata,
                "suggestions": result.suggestions,
            }
        )
