from __future__ import annotations

from typing import Any, cast

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from discounts.api.serializers import DiscountCreateSerializer
from discounts.api.serializers import DiscountSerializer
from discounts.api.serializers import DiscountSettingsSerializer
from discounts.api.serializers import DiscountUpdateSerializer
from discounts.api.serializers import FirstOrderDiscountConfigSerializer
from discounts.models.discount import Discount
from discounts.models.discount_settings import DiscountSettings
from discounts.models.first_order_discount_config import (
    FirstOrderDiscountConfig,
)
from discounts.models.promotional_campaign import PromotionalCampaign
from discounts.permissions import CanManageDiscounts
from discounts.permissions import CanViewDiscounts
from discounts.selectors.discount_selectors import DiscountSelector
from discounts.services.discount_admin_service import DiscountAdminService
from discounts.services.discount_code_generator import (
    DiscountCodeGenerator,
)


UserModel = get_user_model()


def _drf(request) -> Request:
    """
    Return a request object typed as a DRF request.
    """
    return cast(Request, request)


def _user(request: Request):
    """
    Return the authenticated request user.

    Permissions should already reject anonymous users, but this guard keeps
    the view safe when called directly in tests.
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


class AdminDiscountListCreateAPIView(APIView):
    """
    List and create tenant-scoped discounts.
    """

    permission_classes = [CanViewDiscounts]

    def get_permissions(self):
        """
        Return read or write permissions based on request method.
        """
        request = _drf(self.request)

        if request.method == "POST":
            return [CanManageDiscounts()]

        return [CanViewDiscounts()]

    def get(self, request) -> Response:
        """
        Return discounts for the resolved tenant.
        """
        request = _drf(request)
        website = _website(request)

        status_value = request.query_params.get("status")
        origin = request.query_params.get("origin")

        if status_value == "working":
            queryset = DiscountSelector.list_working(website=website)
        elif status_value == "scheduled":
            queryset = DiscountSelector.list_scheduled(website=website)
        elif status_value == "expired":
            queryset = DiscountSelector.list_expired(website=website)
        elif status_value == "archived":
            queryset = DiscountSelector.list_archived(website=website)
        else:
            queryset = DiscountSelector.list_with_usage_counts(
                website=website,
            )

        if origin:
            queryset = queryset.filter(origin=origin)

        serializer = DiscountSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request) -> Response:
        """
        Create a discount for the resolved tenant.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        serializer = DiscountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        eligible_client_ids = data.pop("eligible_client_ids", [])
        generate_code = data.pop("generate_code", False)
        code_prefix = data.pop("code_prefix", "")
        raw_code = data.pop("discount_code", None)
        campaign_id = data.pop("campaign_id", None)

        eligible_clients = self._get_eligible_clients(
            eligible_client_ids=eligible_client_ids,
            website=website,
        )

        discount_code = self._resolve_discount_code(
            website=website,
            generate_code=generate_code,
            code_prefix=code_prefix,
            raw_code=raw_code,
        )
        campaign = self._resolve_campaign(
            website=website,
            campaign_id=campaign_id,
        )

        discount = DiscountAdminService.create_discount(
            website=website,
            created_by=user,
            eligible_clients=eligible_clients,
            discount_code=discount_code,
            campaign=campaign,
            **data,
        )

        response_serializer = DiscountSerializer(discount)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _get_eligible_clients(
        *,
        eligible_client_ids: list[int],
        website,
    ):
        """
        Return eligible clients scoped to the tenant website.
        """
        if not eligible_client_ids:
            return []

        return UserModel.objects.filter(
            id__in=eligible_client_ids,
            website=website,
        )

    @staticmethod
    def _resolve_discount_code(
        *,
        website,
        generate_code: bool,
        code_prefix: str,
        raw_code: str | None,
    ) -> str:
        """
        Return either a generated code or the provided manual code.
        """
        if generate_code:
            return DiscountCodeGenerator.generate_unique(
                website=website,
                prefix=code_prefix or "",
            )

        if not raw_code:
            raise PermissionDenied("Discount code is required.")

        return raw_code

    @staticmethod
    def _resolve_campaign(*, website, campaign_id):
        """
        Return a tenant-scoped campaign when one is provided.
        """
        if campaign_id is None:
            return None

        return get_object_or_404(
            PromotionalCampaign,
            id=campaign_id,
            website=website,
        )


class AdminDiscountDetailAPIView(APIView):
    """
    Retrieve and update a single tenant-scoped discount.
    """

    def get_permissions(self):
        """
        Return read or write permissions based on request method.
        """
        request = _drf(self.request)

        if request.method in {"PUT", "PATCH"}:
            return [CanManageDiscounts()]

        return [CanViewDiscounts()]

    def get(self, request, pk: int) -> Response:
        """
        Return one discount for the resolved tenant.
        """
        discount = self._get_discount(request=request, pk=pk)

        return Response(
            DiscountSerializer(discount).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk: int) -> Response:
        """
        Partially update one discount.
        """
        return self._update(request=request, pk=pk, partial=True)

    def put(self, request, pk: int) -> Response:
        """
        Fully update one discount.
        """
        return self._update(request=request, pk=pk, partial=False)

    def _update(
        self,
        *,
        request,
        pk: int,
        partial: bool,
    ) -> Response:
        """
        Update a tenant-scoped discount through the service layer.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        discount = self._get_discount(request=request, pk=pk)

        serializer = DiscountUpdateSerializer(
            discount,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        eligible_client_ids = data.pop("eligible_client_ids", None)
        data.pop("generate_code", None)
        data.pop("code_prefix", None)

        campaign_id = data.pop("campaign_id", None)

        if campaign_id is not None:
            data["campaign"] = self._resolve_campaign(
                website=website,
                campaign_id=campaign_id,
            )

        eligible_clients = None

        if eligible_client_ids is not None:
            eligible_clients = self._get_eligible_clients(
                eligible_client_ids=eligible_client_ids,
                website=website,
            )

        discount = DiscountAdminService.update_discount(
            discount=discount,
            updated_by=user,
            eligible_clients=eligible_clients,
            **data,
        )

        return Response(
            DiscountSerializer(discount).data,
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_discount(*, request, pk: int) -> Discount:
        """
        Return one discount scoped to request.website.
        """
        request = _drf(request)
        website = _website(request)

        return get_object_or_404(
            DiscountSelector.base_queryset(website=website),
            pk=pk,
        )

    @staticmethod
    def _get_eligible_clients(
        *,
        eligible_client_ids: list[int],
        website,
    ):
        """
        Return eligible clients scoped to the tenant website.
        """
        if not eligible_client_ids:
            return []

        return UserModel.objects.filter(
            id__in=eligible_client_ids,
            website=website,
        )

    @staticmethod
    def _resolve_campaign(*, website, campaign_id):
        """
        Return a tenant-scoped campaign when one is provided.
        """
        if campaign_id is None:
            return None

        return get_object_or_404(
            PromotionalCampaign,
            id=campaign_id,
            website=website,
        )


class AdminDiscountArchiveAPIView(APIView):
    """
    Archive a tenant-scoped discount.
    """

    permission_classes = [CanManageDiscounts]

    def post(self, request, pk: int) -> Response:
        """
        Archive one discount without deleting usage history.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        discount = get_object_or_404(
            DiscountSelector.base_queryset(website=website),
            pk=pk,
        )

        discount = DiscountAdminService.archive_discount(
            discount=discount,
            updated_by=user,
        )

        return Response(
            DiscountSerializer(discount).data,
            status=status.HTTP_200_OK,
        )


class AdminDiscountRestoreAPIView(APIView):
    """
    Restore an archived tenant-scoped discount.
    """

    permission_classes = [CanManageDiscounts]

    def post(self, request, pk: int) -> Response:
        """
        Restore one archived discount.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        discount = get_object_or_404(
            DiscountSelector.base_queryset(website=website),
            pk=pk,
        )

        discount = DiscountAdminService.restore_discount(
            discount=discount,
            updated_by=user,
        )

        return Response(
            DiscountSerializer(discount).data,
            status=status.HTTP_200_OK,
        )


class DiscountSettingsAPIView(APIView):
    """
    Retrieve and update tenant discount settings.
    """

    permission_classes = [CanManageDiscounts]

    def get(self, request) -> Response:
        """
        Return tenant discount settings.
        """
        settings_obj = self._get_settings(request=request)

        return Response(
            DiscountSettingsSerializer(settings_obj).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request) -> Response:
        """
        Partially update tenant discount settings.
        """
        return self._update(request=request, partial=True)

    def put(self, request) -> Response:
        """
        Fully update tenant discount settings.
        """
        return self._update(request=request, partial=False)

    def _update(self, *, request, partial: bool) -> Response:
        """
        Update tenant discount settings.
        """
        request = _drf(request)
        user = _user(request)
        settings_obj = self._get_settings(request=request)

        serializer = DiscountSettingsSerializer(
            settings_obj,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _get_settings(*, request) -> DiscountSettings:
        """
        Return or create tenant discount settings.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        settings_obj, _ = DiscountSettings.objects.get_or_create(
            website=website,
            defaults={
                "created_by": user,
                "updated_by": user,
            },
        )

        return settings_obj


class FirstOrderDiscountConfigAPIView(APIView):
    """
    Retrieve and update tenant first order discount config.
    """

    permission_classes = [CanManageDiscounts]

    def get(self, request) -> Response:
        """
        Return tenant first order discount config.
        """
        config = self._get_config(request=request)

        return Response(
            FirstOrderDiscountConfigSerializer(config).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request) -> Response:
        """
        Partially update first order discount config.
        """
        return self._update(request=request, partial=True)

    def put(self, request) -> Response:
        """
        Fully update first order discount config.
        """
        return self._update(request=request, partial=False)

    def _update(self, *, request, partial: bool) -> Response:
        """
        Update tenant first order discount config.
        """
        request = _drf(request)
        user = _user(request)
        config = self._get_config(request=request)

        serializer = FirstOrderDiscountConfigSerializer(
            config,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def _get_config(*, request) -> FirstOrderDiscountConfig:
        """
        Return or create tenant first order discount config.
        """
        request = _drf(request)
        user = _user(request)
        website = _website(request)

        config, _ = FirstOrderDiscountConfig.objects.get_or_create(
            website=website,
            defaults={
                "created_by": user,
                "updated_by": user,
            },
        )

        return config