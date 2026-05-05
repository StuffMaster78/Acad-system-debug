from __future__ import annotations

from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import CanManageSpecialOrderOverride
from special_orders.api.serializers.override_serializers import (
    AdminOverrideSerializer,
    ApplyAdminOverrideSerializer,
    RejectAdminOverrideSerializer,
    RequestAdminOverrideSerializer,
)
from special_orders.models import SpecialOrderAdminOverride
from special_orders.selectors import SpecialOrderSelector
from special_orders.services.new_services.special_order_admin_override_service import (
    SpecialOrderAdminOverrideService,
)


class RequestAdminOverrideView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderOverride]

    def post(self, request, special_order_id: int):
        serializer = RequestAdminOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        override = SpecialOrderAdminOverrideService.request_override(
            special_order=special_order,
            override_type=str(data["override_type"]),
            requested_by=request.user,
            reason=str(data["reason"]),
            amount=data.get("amount"),
            metadata=cast(dict[str, Any], data.get("metadata", {})),
        )

        return Response(
            AdminOverrideSerializer(override).data,
            status=status.HTTP_201_CREATED,
        )


class ApproveAdminOverrideView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderOverride]

    def post(self, request, override_id: int):
        override = SpecialOrderAdminOverride.objects.select_related(
            "special_order",
        ).get(
            id=override_id,
            website=request.user.website,
        )
        self.check_object_permissions(request, override.special_order)

        override = SpecialOrderAdminOverrideService.approve_override(
            override=override,
            approved_by=request.user,
        )

        return Response(AdminOverrideSerializer(override).data)


class RejectAdminOverrideView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderOverride]

    def post(self, request, override_id: int):
        serializer = RejectAdminOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        override = SpecialOrderAdminOverride.objects.select_related(
            "special_order",
        ).get(
            id=override_id,
            website=request.user.website,
        )
        self.check_object_permissions(request, override.special_order)

        override = SpecialOrderAdminOverrideService.reject_override(
            override=override,
            rejected_by=request.user,
            reason=str(data["reason"]),
        )

        return Response(AdminOverrideSerializer(override).data)


class ApplyAdminOverrideView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderOverride]

    def post(self, request, override_id: int):
        serializer = ApplyAdminOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        override = SpecialOrderAdminOverride.objects.select_related(
            "special_order",
            "delivery_checkpoint",
        ).get(
            id=override_id,
            website=request.user.website,
        )
        self.check_object_permissions(request, override.special_order)

        override = SpecialOrderAdminOverrideService.apply_override(
            override=override,
            applied_by=request.user,
            idempotency_key=str(data.get("idempotency_key", "")) or None,
        )

        return Response(AdminOverrideSerializer(override).data)