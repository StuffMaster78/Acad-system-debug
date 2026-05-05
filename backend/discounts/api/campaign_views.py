from __future__ import annotations

from typing import Any
from typing import cast

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from discounts.api.serializers import AdminCampaignSerializer
from discounts.api.serializers import CampaignCreateUpdateSerializer
from discounts.api.serializers import ClientCampaignCalendarSerializer
from discounts.permissions import CanManageDiscounts
from discounts.permissions import CanUseClientDiscounts
from discounts.permissions import CanViewDiscounts
from discounts.selectors.campaign_selectors import CampaignSelector
from discounts.services.campaign_admin_service import CampaignAdminService
from discounts.services.campaign_lifecycle_service import (
    CampaignLifecycleService,
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


class ClientCampaignCalendarAPIView(APIView):
    """
    Return campaigns for the client-facing calendar.
    """

    permission_classes = [CanUseClientDiscounts]

    def get(self, request) -> Response:
        """
        Return public campaign calendar entries.
        """
        request = _drf(request)
        website = _website(request)

        campaigns = CampaignSelector.list_public_calendar_campaigns(
            website=website,
        )

        return Response(
            {
                "campaigns": ClientCampaignCalendarSerializer(
                    campaigns,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminCampaignListCreateAPIView(APIView):
    """
    List and create promotional campaigns.
    """

    def get_permissions(self):
        """
        Return read/write permissions.
        """
        request = _drf(self.request)

        if request.method == "POST":
            return [CanManageDiscounts()]

        return [CanViewDiscounts()]

    def get(self, request) -> Response:
        """
        Return admin campaign list with metrics.
        """
        request = _drf(request)
        website = _website(request)

        campaigns = CampaignSelector.list_with_metrics(
            website=website,
        )

        return Response(
            {
                "campaigns": AdminCampaignSerializer(
                    campaigns,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request) -> Response:
        """
        Create a campaign.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        serializer = CampaignCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        if "name" not in data:
            return Response(
                {"detail": "name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        campaign = CampaignAdminService.create_campaign(
            website=website,
            created_by=user,
            **data,
        )

        return Response(
            AdminCampaignSerializer(campaign).data,
            status=status.HTTP_201_CREATED,
        )


class AdminCampaignDetailAPIView(APIView):
    """
    Retrieve and update one campaign.
    """

    def get_permissions(self):
        """
        Return read/write permissions.
        """
        request = _drf(self.request)

        if request.method in {"PATCH", "PUT"}:
            return [CanManageDiscounts()]

        return [CanViewDiscounts()]

    def get(self, request, pk: int) -> Response:
        """
        Return one campaign.
        """
        request = _drf(request)
        website = _website(request)
        campaign = self._get_campaign(website=website, pk=pk)

        return Response(
            AdminCampaignSerializer(campaign).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk: int) -> Response:
        """
        Partially update one campaign.
        """
        return self._update(request=request, pk=pk, partial=True)

    def put(self, request, pk: int) -> Response:
        """
        Fully update one campaign.
        """
        return self._update(request=request, pk=pk, partial=False)

    def _update(self, *, request, pk: int, partial: bool) -> Response:
        """
        Update one campaign.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)
        campaign = self._get_campaign(website=website, pk=pk)

        serializer = CampaignCreateUpdateSerializer(
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        campaign = CampaignAdminService.update_campaign(
            campaign=campaign,
            updated_by=user,
            **data,
        )

        return Response(
            AdminCampaignSerializer(campaign).data,
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_campaign(*, website, pk: int):
        """
        Return tenant-scoped campaign.
        """
        return get_object_or_404(
            CampaignSelector.base_queryset(website=website),
            pk=pk,
        )


class AdminCampaignActivateAPIView(APIView):
    """
    Activate a campaign and its linked discounts.
    """

    permission_classes = [CanManageDiscounts]

    def post(self, request, pk: int) -> Response:
        """
        Activate one campaign.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        campaign = get_object_or_404(
            CampaignSelector.base_queryset(website=website),
            pk=pk,
        )

        campaign = CampaignLifecycleService.activate_campaign(
            campaign=campaign,
            updated_by=user,
        )

        return Response(
            AdminCampaignSerializer(campaign).data,
            status=status.HTTP_200_OK,
        )


class AdminCampaignDeactivateAPIView(APIView):
    """
    Deactivate a campaign and its linked discounts.
    """

    permission_classes = [CanManageDiscounts]

    def post(self, request, pk: int) -> Response:
        """
        Deactivate one campaign.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        campaign = get_object_or_404(
            CampaignSelector.base_queryset(website=website),
            pk=pk,
        )

        campaign = CampaignLifecycleService.deactivate_campaign(
            campaign=campaign,
            updated_by=user,
        )

        return Response(
            AdminCampaignSerializer(campaign).data,
            status=status.HTTP_200_OK,
        )


class AdminCampaignArchiveAPIView(APIView):
    """
    Archive a campaign and disable linked discounts.
    """

    permission_classes = [CanManageDiscounts]

    def post(self, request, pk: int) -> Response:
        """
        Archive one campaign.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        campaign = get_object_or_404(
            CampaignSelector.base_queryset(website=website),
            pk=pk,
        )

        campaign = CampaignAdminService.archive_campaign(
            campaign=campaign,
            updated_by=user,
        )

        return Response(
            AdminCampaignSerializer(campaign).data,
            status=status.HTTP_200_OK,
        )


class AdminCampaignRestoreAPIView(APIView):
    """
    Restore an archived campaign.

    Restoring only unarchives the campaign. It does not automatically
    activate the campaign or its linked discounts. Admins can activate it
    explicitly after review.
    """

    permission_classes = [CanManageDiscounts]

    def post(self, request, pk: int) -> Response:
        """
        Restore one archived campaign.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        campaign = get_object_or_404(
            CampaignSelector.base_queryset(website=website),
            pk=pk,
        )

        campaign = CampaignAdminService.restore_campaign(
            campaign=campaign,
            updated_by=user,
        )

        return Response(
            AdminCampaignSerializer(campaign).data,
            status=status.HTTP_200_OK,
        )