"""
Admin-facing pricing config API views.
"""

from __future__ import annotations

from typing import Any
from typing import cast

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from order_pricing_core.api.serializers.pricing_config_serializers import (
    AcademicLevelRateSerializer,
)
from order_pricing_core.api.serializers.pricing_config_serializers import (
    AnalysisLevelRateSerializer,
)
from order_pricing_core.api.serializers.pricing_config_serializers import (
    DeadlineRateSerializer,
)
from order_pricing_core.api.serializers.pricing_config_serializers import (
    DiagramComplexityRateSerializer,
)
from order_pricing_core.api.serializers.pricing_config_serializers import (
    PaperTypeRateSerializer,
)
from order_pricing_core.api.serializers.pricing_config_serializers import (
    SubjectCategorySerializer,
)
from order_pricing_core.api.serializers.pricing_config_serializers import (
    SubjectRateSerializer,
)
from order_pricing_core.api.serializers.pricing_config_serializers import (
    WebsitePricingProfileSerializer,
)
from order_pricing_core.api.serializers.pricing_config_serializers import (
    WorkTypeRateSerializer,
)
from order_pricing_core.api.serializers.pricing_config_serializers import (
    WriterLevelRateSerializer,
)
from order_pricing_core.models import AcademicLevelRate
from order_pricing_core.models import AnalysisLevelRate
from order_pricing_core.models import DeadlineRate
from order_pricing_core.models import DiagramComplexityRate
from order_pricing_core.models import PaperTypeRate
from order_pricing_core.models import SubjectCategory
from order_pricing_core.models import SubjectRate
from order_pricing_core.models import WorkTypeRate
from order_pricing_core.models import WriterLevelRate
from order_pricing_core.permissions import CanManagePricingConfig
from order_pricing_core.selectors.pricing_dimensions_selectors import (
    get_academic_level_rate_by_id,
)
from order_pricing_core.selectors.pricing_dimensions_selectors import (
    get_analysis_level_rate_by_id,
)
from order_pricing_core.selectors.pricing_dimensions_selectors import (
    get_deadline_rate_by_id,
)
from order_pricing_core.selectors.pricing_dimensions_selectors import (
    get_diagram_complexity_rate_by_id,
)
from order_pricing_core.selectors.pricing_dimensions_selectors import (
    get_paper_type_rate_by_id,
)
from order_pricing_core.selectors.pricing_dimensions_selectors import (
    get_subject_category_by_id,
)
from order_pricing_core.selectors.pricing_dimensions_selectors import (
    get_subject_rate_by_id,
)
from order_pricing_core.selectors.pricing_dimensions_selectors import (
    get_work_type_rate_by_id,
)
from order_pricing_core.selectors.pricing_dimensions_selectors import (
    get_writer_level_rate_by_id,
)
from order_pricing_core.selectors.pricing_profile_selectors import (
    get_active_pricing_profile,
)
from order_pricing_core.services.pricing_dimension_admin_service import (
    PricingDimensionAdminService,
)
from order_pricing_core.services.pricing_profile_admin_service import (
    PricingProfileAdminService,
)
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_deadline_rate,
)
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_non_negative_amount,
)
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_positive_multiplier,
)
from order_pricing_core.validators.pricing_dimension_validators import (
    validate_subject_rate,
)

    
class WebsitePricingProfileView(APIView):
    """
    Retrieve or update the active pricing profile.
    """

    permission_classes = [CanManagePricingConfig]

    def get(self, request: Request) -> Response:
        profile = get_active_pricing_profile(website=request.website)

        return Response(
            {
                "id": profile.pk,
                "profile_name": profile.profile_name,
                "currency": profile.currency,
                "base_price_per_page": profile.base_price_per_page,
                "base_price_per_slide": profile.base_price_per_slide,
                "base_price_per_diagram": profile.base_price_per_diagram,
                "double_spacing_multiplier": (
                    profile.double_spacing_multiplier
                ),
                "single_spacing_multiplier": (
                    profile.single_spacing_multiplier
                ),
                "preferred_writer_fee": profile.preferred_writer_fee,
                "minimum_paper_order_charge": (
                    profile.minimum_paper_order_charge
                ),
                "minimum_design_order_charge": (
                    profile.minimum_design_order_charge
                ),
                "minimum_diagram_order_charge": (
                    profile.minimum_diagram_order_charge
                ),
                "max_pages_per_hour": profile.max_pages_per_hour,
                "extra_hour_per_extra_page": (
                    profile.extra_hour_per_extra_page
                ),
                "rush_recommendation_only": (
                    profile.rush_recommendation_only
                ),
                "is_active": profile.is_active,
                "allow_customization": profile.allow_customization,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request: Request) -> Response:
        serializer = WebsitePricingProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        profile = PricingProfileAdminService.update_active_profile(
            website=request.website,
            data=data,
        )

        return Response(
            {
                "id": profile.pk,
                "profile_name": profile.profile_name,
                "currency": profile.currency,
            },
            status=status.HTTP_200_OK,
        )


class AcademicLevelRateListCreateView(APIView):
    """
    List or create academic level rates.
    """

    permission_classes = [CanManagePricingConfig]

    def get(self, request: Request) -> Response:
        items = AcademicLevelRate.objects.filter(
            website=request.website,
        ).order_by("sort_order", "id")

        return Response(
            [
                {
                    "id": item.pk,
                    "code": item.code,
                    "label": item.label,
                    "multiplier": item.multiplier,
                    "sort_order": item.sort_order,
                    "is_active": item.is_active,
                }
                for item in items
            ],
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request) -> Response:
        serializer = AcademicLevelRateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)
        item = PricingDimensionAdminService.create_academic_level_rate(
            website=request.website,
            data=data,
        )

        return Response(
            {
                "id": item.pk,
                "code": item.code,
                "label": item.label,
            },
            status=status.HTTP_201_CREATED,
        )


class AcademicLevelRateDetailView(APIView):
    """
    Retrieve, update, or delete an academic level rate.
    """

    permission_classes = [CanManagePricingConfig]

    def get(self, request: Request, item_id: int) -> Response:
        item = get_academic_level_rate_by_id(
            website=request.website,
            item_id=item_id,
        )

        return Response(
            {
                "id": item.pk,
                "code": item.code,
                "label": item.label,
                "multiplier": item.multiplier,
                "sort_order": item.sort_order,
                "is_active": item.is_active,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request: Request, item_id: int) -> Response:
        item = get_academic_level_rate_by_id(
            website=request.website,
            item_id=item_id,
        )

        serializer = AcademicLevelRateSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        if "multiplier" in data:
            validate_positive_multiplier(
                multiplier=data["multiplier"],
            )

        for field, value in data.items():
            setattr(item, field, value)

        item.save()

        return Response(
            {
                "id": item.pk,
                "code": item.code,
                "label": item.label,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request, item_id: int) -> Response:
        item = get_academic_level_rate_by_id(
            website=request.website,
            item_id=item_id,
        )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)