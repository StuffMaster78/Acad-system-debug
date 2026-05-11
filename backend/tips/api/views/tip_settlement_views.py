from rest_framework.views import APIView
from rest_framework.response import Response

from typing import cast
from rest_framework.permissions import IsAuthenticated

from tips.services.tip_settlement_engine import TipSettlementEngine
from tips.api.serializers.tip_settlement_snapshot_serializers import (
    TipSettlementSnapshotSerializer,
)
from tips.api.serializers.tip_serializers import TipSettleSerializer
from tips.models.tip import Tip


class TipSettleAPIView(APIView):

    def post(self, request):
        permission_classes = [IsAuthenticated]

        serializer = TipSettleSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        data = cast(
            dict,
            serializer.validated_data,
        )

        tip = Tip.objects.get(pk=data["tip_id"])

        settled_tip = TipSettlementEngine.settle_tip(
            tip=tip,
            triggered_by=request.user,
        )

        snapshot = {
            "tip_id": settled_tip.pk,
            "gross_amount_cents": settled_tip.gross_amount_cents,
            "writer_share_cents": settled_tip.writer_share_cents,
            "platform_fee_cents": settled_tip.platform_fee_cents,
            "settled_at": settled_tip.settled_at,
            "settlement_status": settled_tip.status,
        }

        serializer = TipSettlementSnapshotSerializer(data=snapshot)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)