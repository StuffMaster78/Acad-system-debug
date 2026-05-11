from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from tips.models.tip_policy_snapshot import (
    TipPolicySnapshot,
)

from tips.models.tip_settlement_snapshot import (
    TipSettlementSnapshot,
)

from tips.api.serializers.tip_policy_snapshot_serializers import (
    TipPolicySnapshotSerializer,
)

from tips.api.serializers.tip_settlement_snapshot_serializers import (
    TipSettlementSnapshotSerializer,
)


class AdminPolicySnapshotListAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        snapshots = (
            TipPolicySnapshot.objects
            .order_by("-created_at")[:100]
        )

        serializer = (
            TipPolicySnapshotSerializer(
                snapshots,
                many=True,
            )
        )

        return Response(serializer.data)


class AdminSettlementSnapshotListAPIView(
    APIView
):

    permission_classes = [IsAdminUser]

    def get(self, request):

        snapshots = (
            TipSettlementSnapshot.objects
            .order_by("-created_at")[:100]
        )

        serializer = (
            TipSettlementSnapshotSerializer(
                snapshots,
                many=True,
            )
        )

        return Response(serializer.data)