from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)


class TrustScoreDetailView(
    APIView,
):
    """
    Return writer trust score details.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """
        Fetch trust score payload.
        """

        writer_id = (
            self.kwargs.get(
                "writer_id",
            )
        )

        snapshot = (
            WriterReputationSnapshot.objects
            .filter(
                writer_id=writer_id,
            )
            .first()
        )

        if snapshot is None:
            return Response(
                {
                    "detail": (
                        "Snapshot not found."
                    ),
                },
                status=404,
            )

        return Response(
            {
                "writer_id": writer_id,
                "rating": str(
                    snapshot.rating,
                ),
                "review_count": (
                    snapshot.review_count
                ),
                "trust_score": (
                    snapshot.metadata.get(
                        "trust_score",
                        "0.00",
                    )
                ),
                "percentile_rank": (
                    snapshot.metadata.get(
                        "percentile_rank",
                        "0.00",
                    )
                ),
                "leaderboard_position": (
                    snapshot.metadata.get(
                        "leaderboard_position",
                    )
                ),
                "metadata": (
                    snapshot.metadata
                ),
            },
        )