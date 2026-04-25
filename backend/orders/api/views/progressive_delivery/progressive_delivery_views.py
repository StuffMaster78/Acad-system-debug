from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.serializers.progressive_delivery.progressive_delivery_serializers import (
    CreateProgressivePlanSerializer,
)
from orders.models import Order
from orders.services.progressive_delivery_service import (
    ProgressiveDeliveryService,
)


class CreateProgressivePlanView(GenericAPIView):
    serializer_class = CreateProgressivePlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, order_id: int) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(Any, request.user)

        order = get_object_or_404(
            Order,
            pk=order_id,
            website=user.website,
        )

        plan = ProgressiveDeliveryService.create_plan(
            order=order,
            milestones=serializer.validated_data["milestones"],
            created_by=user,
        )

        return Response(
            {
                "plan_id": plan.pk,
                "milestones": len(serializer.validated_data["milestones"]),
            },
            status=status.HTTP_201_CREATED,
        )