from __future__ import annotations

from typing import Any
from typing import cast

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from discounts.api.serializers import DiscountSpendTierCreateSerializer
from discounts.api.serializers import DiscountSpendTierSerializer
from discounts.models.discount_spend_tier import DiscountSpendTier
from discounts.permissions import CanManageDiscounts
from discounts.permissions import CanViewDiscounts
from discounts.services.discount_spend_tier_admin_service import (
    DiscountSpendTierAdminService,
)


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


class AdminSpendTierListCreateAPIView(APIView):
    """
    List and create spend tier discounts.
    """

    def get_permissions(self):
        """
        Return read or write permission based on request method.
        """
        request = _drf(self.request)

        if request.method == "POST":
            return [CanManageDiscounts()]

        return [CanViewDiscounts()]

    def get(self, request) -> Response:
        """
        Return tenant-scoped spend tiers.
        """
        request = _drf(request)
        website = _website(request)

        queryset = (
            DiscountSpendTier.objects
            .filter(website=website)
            .select_related("website", "discount")
            .order_by("-minimum_lifetime_spend")
        )

        return Response(
            {
                "spend_tiers": DiscountSpendTierSerializer(
                    queryset,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request) -> Response:
        """
        Create a spend tier and linked discount.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        serializer = DiscountSpendTierCreateSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)
        data.pop("website_id", None)

        tier = DiscountSpendTierAdminService.create_tier(
            website=website,
            created_by=user,
            **data,
        )

        return Response(
            DiscountSpendTierSerializer(tier).data,
            status=status.HTTP_201_CREATED,
        )


class AdminSpendTierDetailAPIView(APIView):
    """
    Retrieve and update a spend tier discount.
    """

    def get_permissions(self):
        """
        Return read or write permission based on request method.
        """
        request = _drf(self.request)

        if request.method in {"PUT", "PATCH"}:
            return [CanManageDiscounts()]

        return [CanViewDiscounts()]

    def get(self, request, pk: int) -> Response:
        """
        Return one tenant-scoped spend tier.
        """
        request = _drf(request)
        website = _website(request)
        tier = self._get_tier(website=website, pk=pk)

        return Response(
            DiscountSpendTierSerializer(tier).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk: int) -> Response:
        """
        Partially update one spend tier.
        """
        return self._update(
            request=request,
            pk=pk,
            partial=True,
        )

    def put(self, request, pk: int) -> Response:
        """
        Fully update one spend tier.
        """
        return self._update(
            request=request,
            pk=pk,
            partial=False,
        )

    def _update(
        self,
        *,
        request,
        pk: int,
        partial: bool,
    ) -> Response:
        """
        Update spend tier and linked discount.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)
        tier = self._get_tier(website=website, pk=pk)

        serializer = DiscountSpendTierCreateSerializer(
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)
        data.pop("website_id", None)

        tier = DiscountSpendTierAdminService.update_tier(
            tier=tier,
            updated_by=user,
            **data,
        )

        return Response(
            DiscountSpendTierSerializer(tier).data,
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_tier(*, website, pk: int) -> DiscountSpendTier:
        """
        Return one tenant-scoped spend tier.
        """
        queryset = DiscountSpendTier.objects.filter(
            website=website,
        ).select_related(
            "website",
            "discount",
        )

        return get_object_or_404(queryset, pk=pk)