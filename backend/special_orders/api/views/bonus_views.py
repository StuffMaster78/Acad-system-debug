from __future__ import annotations

from typing import Any, cast

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import CanManageSpecialOrderOverride
from special_orders.api.serializers.bonus_serializers import (
    RequestWriterBonusSerializer,
)
from special_orders.selectors import SpecialOrderSelector
from special_orders.services.new_services.special_order_bonus_service import (
    SpecialOrderBonusService,
)


class RequestWriterBonusView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderOverride]

    def post(self, request, special_order_id: int):
        serializer = RequestWriterBonusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        User = get_user_model()
        writer = User.objects.get(
            id=int(data["writer_id"]),
            website=request.user.website,
        )

        result = SpecialOrderBonusService.request_writer_bonus(
            special_order=special_order,
            writer=writer,
            amount=data["amount"],
            category=str(data["category"]),
            reason=str(data["reason"]),
            requested_by=request.user,
            metadata=cast(dict[str, Any], data.get("metadata", {})),
        )

        return Response(result, status=status.HTTP_201_CREATED)