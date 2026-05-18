from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)


class WriterReputationSnapshotView(
    APIView,
):
    """
    Writer reputation snapshot endpoint.
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
        Return reputation snapshot.
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

        payload = {
            "writer_id": (
                snapshot.writer_id
            ),
            "rating": (
                snapshot.rating
            ),
            "review_count": (
                snapshot.review_count
            ),
            "verified_review_count": (
                snapshot.verified_review_count
            ),
            "percentile_rank": (
                snapshot.percentile_rank
            ),
            "trust_score": (
                snapshot.trust_score
            ),
            "rating_velocity": (
                snapshot.rating_velocity
            ),
            "metadata": (
                snapshot.metadata
            ),
            "updated_at": (
                snapshot.updated_at
            ),
        }

        return Response(
            payload,
        )