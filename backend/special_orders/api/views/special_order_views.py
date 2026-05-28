from __future__ import annotations
from rest_framework.permissions import IsAuthenticated

from typing import Any, cast

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import (
    CanCreateSpecialOrder,
    CanViewSpecialOrder,
)
from special_orders.api.serializers import (
    CreateFixedSpecialOrderSerializer,
    CreateQuotedSpecialOrderSerializer,
    SpecialOrderDetailSerializer,
    SpecialOrderListSerializer,
)
from special_orders.api.serializers.config_serializers import (
    PredefinedSpecialOrderConfigSerializer,
)
from special_orders.selectors import (
    SpecialOrderConfigSelector,
    SpecialOrderSelector,
)
from special_orders.services.new_services.special_order_creation_service import (
    SpecialOrderCreationService,
)


class ListPredefinedSpecialOrderConfigsView(APIView):
    """
    List active predefined special order configs for the current website.
    Used by clients to browse fixed-price express order options.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        configs = SpecialOrderConfigSelector.list_predefined_configs(
            website=request.user.website,
            active_only=True,
        )
        serializer = PredefinedSpecialOrderConfigSerializer(configs, many=True)
        return Response(serializer.data)


class SpecialOrderListView(APIView):
    """
    List special orders for the current portal user.
    """

    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def get(self, request):
        user = request.user
        website = user.website

        if getattr(user, "role", "") == "writer":
            queryset = SpecialOrderSelector.list_for_writer(
                website=website,
                writer=user,
            )
        elif getattr(user, "role", "") == "client":
            queryset = SpecialOrderSelector.list_for_client(
                website=website,
                client=user,
            )
        else:
            queryset = SpecialOrderSelector.list_for_staff(
                website=website,
            )

        serializer = SpecialOrderListSerializer(queryset, many=True)
        return Response(serializer.data)


class SpecialOrderDetailView(APIView):
    """
    Retrieve one tenant-scoped special order.
    """

    permission_classes = [CanViewSpecialOrder]

    def get(self, request, special_order_id: int):
        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )

        self.check_object_permissions(request, special_order)

        serializer = SpecialOrderDetailSerializer(special_order)
        return Response(serializer.data)


class CreateQuotedSpecialOrderView(APIView):
    """
    Create an estimated or quoted special order inquiry.
    """

    permission_classes = [IsAuthenticated, CanCreateSpecialOrder]

    def post(self, request):
        serializer = CreateQuotedSpecialOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderCreationService.create_quoted_order(
            website=request.user.website,
            client=request.user,
            title=str(data["title"]),
            inquiry_details=str(data.get("inquiry_details", "")),
            budget=data.get("budget"),
            duration_days=data.get("duration_days"),
            currency=str(data.get("currency", "USD")),
            created_by=request.user,
        )

        response_serializer = SpecialOrderDetailSerializer(special_order)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class CreateFixedSpecialOrderView(APIView):
    """
    Create a fixed special order from predefined config and duration.
    """

    permission_classes = [IsAuthenticated, CanCreateSpecialOrder]

    def post(self, request):
        serializer = CreateFixedSpecialOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        predefined_config = SpecialOrderConfigSelector.get_predefined_config(
            website=request.user.website,
            config_id=int(data["predefined_config_id"]),
        )
        predefined_duration = SpecialOrderConfigSelector.get_duration(
            website=request.user.website,
            duration_id=int(data["predefined_duration_id"]),
        )

        special_order = SpecialOrderCreationService.create_fixed_order(
            website=request.user.website,
            client=request.user,
            predefined_config=predefined_config,
            predefined_duration=predefined_duration,
            title=str(data.get("title", "")) or None,
            inquiry_details=str(data.get("inquiry_details", "")),
            currency=str(data.get("currency", "USD")),
            platform=str(data.get("platform", "")),
            writer_level=str(data.get("writer_level", "")),
            coupon_code=str(data.get("coupon_code", "")),
            created_by=request.user,
        )

        response_serializer = SpecialOrderDetailSerializer(special_order)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )