from __future__ import annotations

from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import (
    CanDownloadSpecialOrderDeliverable,
    CanUploadSpecialOrderDeliverable,
    CanViewSpecialOrder,
)
from special_orders.api.serializers.delivery_serializers import (
    CreateDeliverableSerializer,
    DeliveryCheckpointSerializer,
    SpecialOrderDeliverableSerializer,
)
from special_orders.integrations.files_bridge import SpecialOrderFilesBridge
from special_orders.models import SpecialOrderDeliverable
from special_orders.selectors import (
    SpecialOrderDeliverySelector,
    SpecialOrderSelector,
)


class CreateDeliverableView(APIView):
    permission_classes = [IsAuthenticated, CanUploadSpecialOrderDeliverable]

    def post(self, request, special_order_id: int):
        serializer = CreateDeliverableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        deliverable = SpecialOrderFilesBridge.create_deliverable_from_file(
            special_order=special_order,
            file_reference=str(data["file_reference"]),
            title=str(data["title"]),
            uploaded_by=request.user,
            description=str(data.get("description", "")),
            metadata=cast(dict[str, Any], data.get("metadata", {})),
        )

        return Response(
            SpecialOrderDeliverableSerializer(deliverable).data,
            status=status.HTTP_201_CREATED,
        )


class ListDeliverablesView(APIView):
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def get(self, request, special_order_id: int):
        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        deliverables = SpecialOrderDeliverySelector.list_deliverables(
            website=request.user.website,
            special_order=special_order,
        )

        return Response(
            SpecialOrderDeliverableSerializer(deliverables, many=True).data,
        )


class DownloadDeliverableView(APIView):
    permission_classes = [IsAuthenticated, CanDownloadSpecialOrderDeliverable]

    def post(self, request, deliverable_id: int):
        deliverable = SpecialOrderDeliverable.objects.select_related(
            "special_order",
        ).get(
            id=deliverable_id,
            website=request.user.website,
        )

        self.check_object_permissions(request, deliverable)

        signed_url = SpecialOrderFilesBridge.get_guarded_download_url(
            deliverable=deliverable,
            requested_by=request.user,
            request=request,
        )

        return Response(
            {
                "download_url": signed_url,
            }
        )


class ListDeliveryCheckpointsView(APIView):
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def get(self, request, special_order_id: int):
        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        checkpoints = SpecialOrderDeliverySelector.list_checkpoints(
            website=request.user.website,
            special_order=special_order,
        )

        return Response(
            DeliveryCheckpointSerializer(checkpoints, many=True).data,
        )