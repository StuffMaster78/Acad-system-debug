from __future__ import annotations

from typing import Any
from typing import cast

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from discounts.api.serializers import CampaignCloneSerializer
from discounts.api.serializers import DiscountCloneSerializer
from discounts.api.serializers import DiscountSerializer
from discounts.api.serializers import PromotionalCampaignSerializer
from discounts.models.discount import Discount
from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.permissions import CanManageDiscounts
from discounts.services.discount_clone_service import DiscountCloneService
from websites.models.websites import Website


def _drf(request) -> Request:
    """
    Return request as a DRF request.
    """
    return cast(Request, request)


def _user(request: Request):
    """
    Return authenticated request user.
    """
    user = request.user

    if not user or not user.is_authenticated:
        raise PermissionDenied("Authentication required.")

    return cast(Any, user)


def _website(request: Request):
    """
    Return tenant website resolved by middleware.
    """
    website = getattr(request, "website", None)

    if website is None:
        raise PermissionDenied("Tenant website could not be resolved.")

    return website


class AdminDiscountCloneAPIView(APIView):
    """
    Clone one discount into another website.
    """

    permission_classes = [CanManageDiscounts]

    def post(self, request) -> Response:
        """
        Clone a discount into a target tenant website.
        """
        request = _drf(request)
        user = _user(request)
        source_website = _website(request)

        serializer = DiscountCloneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        source_discount = self._get_source_discount(
            source_website=source_website,
            discount_id=data["source_discount_id"],
        )
        target_website = self._get_target_website(
            website_id=data["target_website_id"],
        )
        target_campaign = self._get_target_campaign(
            target_website=target_website,
            campaign_id=data.get("target_campaign_id"),
        )

        discount = DiscountCloneService.clone_discount(
            source_discount=source_discount,
            target_website=target_website,
            created_by=user,
            new_code=data.get("new_code"),
            target_campaign=target_campaign,
        )

        return Response(
            DiscountSerializer(discount).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _get_source_discount(
        *,
        source_website,
        discount_id: int,
    ) -> Discount:
        """
        Return discount scoped to the current request tenant.

        This prevents cloning discounts from websites the actor should not
        be operating from.
        """
        queryset = Discount.objects.select_related(
            "website",
            "campaign",
        ).filter(
            website=source_website,
            is_deleted=False,
        )

        return get_object_or_404(queryset, id=discount_id)

    @staticmethod
    def _get_target_website(*, website_id: int) -> Website:
        """
        Resolve clone target website.
        """
        return get_object_or_404(Website, id=website_id)

    @staticmethod
    def _get_target_campaign(
        *,
        target_website,
        campaign_id: int | None,
    ) -> PromotionalCampaign | None:
        """
        Resolve optional target campaign scoped to target website.
        """
        if not campaign_id:
            return None

        return get_object_or_404(
            PromotionalCampaign,
            id=campaign_id,
            website=target_website,
        )


class AdminCampaignCloneAPIView(APIView):
    """
    Clone one campaign and its discounts into another website.
    """

    permission_classes = [CanManageDiscounts]

    def post(self, request) -> Response:
        """
        Clone a campaign into a target tenant website.
        """
        request = _drf(request)
        user = _user(request)
        source_website = _website(request)

        serializer = CampaignCloneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        source_campaign = self._get_source_campaign(
            source_website=source_website,
            campaign_id=data["source_campaign_id"],
        )
        target_website = self._get_target_website(
            website_id=data["target_website_id"],
        )

        campaign = DiscountCloneService.clone_campaign(
            source_campaign=source_campaign,
            target_website=target_website,
            created_by=user,
            new_name=data.get("new_name"),
            new_slug=data.get("new_slug"),
        )

        return Response(
            PromotionalCampaignSerializer(campaign).data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _get_source_campaign(
        *,
        source_website,
        campaign_id: int,
    ) -> PromotionalCampaign:
        """
        Return source campaign scoped to the current request tenant.
        """
        queryset = PromotionalCampaign.objects.filter(
            website=source_website,
        ).prefetch_related("discounts")

        return get_object_or_404(queryset, id=campaign_id)

    @staticmethod
    def _get_target_website(*, website_id: int) -> Website:
        """
        Resolve clone target website.
        """
        return get_object_or_404(Website, id=website_id)