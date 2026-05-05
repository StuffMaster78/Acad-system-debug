from __future__ import annotations

from typing import cast

from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from discounts.api.serializers import DiscountSerializer
from discounts.permissions import CanViewDiscountDashboard
from discounts.selectors.discount_dashboard_selectors import (
    DiscountDashboardSelector,
)
from discounts.selectors.discount_selectors import DiscountSelector


def _drf(request) -> Request:
    """
    Return request as a DRF request.
    """
    return cast(Request, request)


def _website(request: Request):
    """
    Return tenant website resolved by middleware.
    """
    website = getattr(request, "website", None)

    if website is None:
        raise PermissionDenied("Tenant website could not be resolved.")

    return website


class DiscountDashboardSummaryAPIView(APIView):
    """
    Return discount dashboard summary metrics.
    """

    permission_classes = [CanViewDiscountDashboard]

    def get(self, request) -> Response:
        """
        Return tenant-scoped discount summary.
        """
        request = _drf(request)
        website = _website(request)

        data = DiscountDashboardSelector.get_summary(
            website=website,
        )

        return Response(data, status=status.HTTP_200_OK)


class DiscountDashboardWorkingAPIView(APIView):
    """
    Return currently usable discounts.
    """

    permission_classes = [CanViewDiscountDashboard]

    def get(self, request) -> Response:
        """
        Return working discounts for the tenant.
        """
        request = _drf(request)
        website = _website(request)

        queryset = DiscountSelector.list_working(
            website=website,
        )
        serializer = DiscountSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DiscountDashboardExpiringSoonAPIView(APIView):
    """
    Return discounts expiring soon.
    """

    permission_classes = [CanViewDiscountDashboard]

    def get(self, request) -> Response:
        """
        Return discounts expiring within a day window.
        """
        request = _drf(request)
        website = _website(request)
        days = self._get_positive_int(
            value=request.query_params.get("days"),
            default=7,
        )

        queryset = DiscountDashboardSelector.list_expiring_soon(
            website=website,
            days=days,
        )
        serializer = DiscountSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _get_positive_int(*, value, default: int) -> int:
        """
        Return a positive integer query param or fallback default.
        """
        if value is None:
            return default

        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return default

        if parsed <= 0:
            return default

        return parsed


class DiscountDashboardTopPerformingAPIView(APIView):
    """
    Return top performing discounts.
    """

    permission_classes = [CanViewDiscountDashboard]

    def get(self, request) -> Response:
        """
        Return top discounts by usage.
        """
        request = _drf(request)
        website = _website(request)
        limit = self._get_positive_int(
            value=request.query_params.get("limit"),
            default=10,
        )

        queryset = DiscountDashboardSelector.list_top_performing(
            website=website,
            limit=limit,
        )
        serializer = DiscountSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _get_positive_int(*, value, default: int) -> int:
        """
        Return a positive integer query param or fallback default.
        """
        if value is None:
            return default

        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return default

        if parsed <= 0:
            return default

        return parsed


class DiscountDashboardUnusedAPIView(APIView):
    """
    Return active discounts that have never been used.
    """

    permission_classes = [CanViewDiscountDashboard]

    def get(self, request) -> Response:
        """
        Return unused working discounts.
        """
        request = _drf(request)
        website = _website(request)

        queryset = DiscountDashboardSelector.list_unused_working(
            website=website,
        )
        serializer = DiscountSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DiscountDashboardByOriginAPIView(APIView):
    """
    Return discount counts grouped by origin.
    """

    permission_classes = [CanViewDiscountDashboard]

    def get(self, request) -> Response:
        """
        Return grouped discount origin data.
        """
        request = _drf(request)
        website = _website(request)

        data = DiscountDashboardSelector.group_by_origin(
            website=website,
        )

        return Response(list(data), status=status.HTTP_200_OK)