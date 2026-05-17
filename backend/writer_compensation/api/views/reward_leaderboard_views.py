# writer_compensation/api/views/reward_leaderboard_views.py

from __future__ import annotations

from typing import cast
from rest_framework.request import Request
from rest_framework.generics import ListAPIView

from reputation_system.services.writer_leaderboard_service import (
    WriterLeaderboardService,
)
from writer_compensation.pagination.reward_pagination import (
    RewardPagination,
)
from writer_compensation.permissions.reward_permissions import (
    IsRewardViewer,
)
from writer_compensation.api.serializers.reward_leaderboard_serializer import (
    RewardLeaderboardSerializer,
)
from writer_management.models.writer_achievement import (
    WriterAchievement,
)


class RewardLeaderboardView(
    ListAPIView,
):
    """
    Public leaderboard API.

    Powers:
        - competitions
        - writer dashboards
        - elite discovery
        - routing intelligence
    """

    serializer_class = (
        RewardLeaderboardSerializer
    )

    permission_classes = [
        IsRewardViewer,
    ]

    pagination_class = (
        RewardPagination
    )

    def get_queryset( # type: ignore[override]
        self,
    ):
        """
        Return leaderboard projections.
        """
        request = cast(Request, self.request)
        limit = int(
            request.query_params.get(
                "limit",
                100,
            )
        )

        leaderboard = (
            WriterLeaderboardService
            .global_leaderboard(
                limit=limit,
            )
        )

        results = []

        for index, snapshot in enumerate(
            leaderboard,
            start=1,
        ):
            achievements = (
                WriterAchievement.objects
                .filter(
                    writer=snapshot.writer,
                )
                .values_list(
                    "title",
                    flat=True,
                )
            )

            results.append(
                {
                    "writer_id": (
                        snapshot.writer.pk
                    ),
                    "writer_name": (
                        snapshot.writer.pen_name
                    ),
                    "rating": (
                        snapshot.rating
                    ),
                    "review_count": (
                        snapshot.review_count
                    ),
                    "percentile_rank": (
                        snapshot.percentile_rank
                    ),
                    "trust_score": (
                        snapshot.trust_score
                    ),
                    "leaderboard_position": (
                        index
                    ),
                    "completed_orders": (
                        snapshot.completed_orders,
                    ),
                    "badges": list(
                        achievements,
                    ),
                }
            )

        return results