# tips/api/views/admin_tip_idempotency_views.py

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from tips.models.tip_idempotency import (
    TipIdempotencyKey,
)


class AdminTipIdempotencyListAPIView(
    APIView
):

    permission_classes = [IsAdminUser]

    def get(self, request):

        keys = (
            TipIdempotencyKey.objects
            .select_related("tip", "sender")
            .order_by("-created_at")[:100]
        )

        data = [
            {
                "id": key.pk,
                "key": key.key,
                "tip_id": getattr(
                    key.tip,
                    "pk",
                    None,
                ),
                "sender_id": getattr(
                    key.sender,
                    "pk",
                    None,
                ),
                "created_at": key.created_at,
            }
            for key in keys
        ]

        return Response(data)