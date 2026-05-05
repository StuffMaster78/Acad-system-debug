from __future__ import annotations

from typing import Any
from typing import cast

from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from discounts.api.serializers import AvailableDiscountSerializer
from discounts.api.serializers import DiscountApplyRequestSerializer
from discounts.api.serializers import DiscountPreviewRequestSerializer
from discounts.api.serializers import ResolvedDiscountSerializer
from discounts.exceptions import DiscountError
from discounts.permissions import CanUseClientDiscounts
from discounts.services.available_discount_service import (
    AvailableDiscountService,
)
from discounts.services.discount_application_service import (
    DiscountApplicationService,
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


class AvailableDiscountListAPIView(APIView):
    """
    List selectable discounts for the authenticated client.
    """

    permission_classes = [CanUseClientDiscounts]

    def post(self, request) -> Response:
        """
        Return usable discounts for a checkout subtotal.
        """
        request = _drf(request)
        client = _user(request)
        website = _website(request)

        serializer = DiscountPreviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        discounts = AvailableDiscountService.list_available_for_client(
            website=website,
            client=client,
            subtotal=data["subtotal"],
            lifetime_spend=data.get("lifetime_spend"),
        )

        return Response(
            {
                "discounts": AvailableDiscountSerializer(
                    discounts,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class DiscountPreviewAPIView(APIView):
    """
    Preview the best available discount for a client checkout.
    """

    permission_classes = [CanUseClientDiscounts]

    def post(self, request) -> Response:
        """
        Resolve a discount without recording usage.
        """
        request = _drf(request)
        client = _user(request)
        website = _website(request)

        serializer = DiscountPreviewRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        try:
            resolved = DiscountApplicationService.preview(
                website=website,
                client=client,
                subtotal=data["subtotal"],
                payable_type=data["payable_type"],
                has_prior_paid_purchase=data[
                    "has_prior_paid_purchase"
                ],
                entered_code=data.get("entered_code"),
                lifetime_spend=data.get("lifetime_spend"),
            )
        except DiscountError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if resolved is None:
            return Response(
                {"discount": None},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"discount": ResolvedDiscountSerializer(resolved).data},
            status=status.HTTP_200_OK,
        )


class DiscountApplyAPIView(APIView):
    """
    Apply a resolved discount to a payable object.
    """

    permission_classes = [CanUseClientDiscounts]

    def post(self, request) -> Response:
        """
        Resolve and persist discount usage.
        """
        request = _drf(request)
        client = _user(request)
        website = _website(request)

        serializer = DiscountApplyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        try:
            usage = DiscountApplicationService.apply(
                website=website,
                client=client,
                subtotal=data["subtotal"],
                payable_type=data["payable_type"],
                payable_id=data["payable_id"],
                has_prior_paid_purchase=data[
                    "has_prior_paid_purchase"
                ],
                entered_code=data.get("entered_code"),
                lifetime_spend=data.get("lifetime_spend"),
                metadata=data.get("metadata"),
            )
        except DiscountError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if usage is None:
            return Response(
                {"discount": None},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "discount_code": usage.discount_code,
                "discount_amount": usage.discount_amount,
                "final_amount": usage.final_amount,
                "origin": usage.origin,
            },
            status=status.HTTP_201_CREATED,
        )