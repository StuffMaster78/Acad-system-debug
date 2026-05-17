from __future__ import annotations

from django.db.models import QuerySet
from typing import cast
from rest_framework.request import Request

from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView

from writer_compensation.filters.rewards_filters import (
    WriterRewardFilter,
)
from writer_compensation.pagination.reward_pagination import (
    RewardPagination,
)
from writer_compensation.permissions.reward_permissions import (
    IsRewardViewer,
)
from writer_compensation.api.serializers.writer_reward_serializer import (
    WriterRewardSerializer,
)
from writer_compensation.selectors.reward_api_selectors import (
    RewardAPISelectors,
)
from writer_compensation.models.writer_reward import (
    WriterReward,
)


class WriterRewardListView(
    ListAPIView,
):
    """
    List issued writer rewards.

    Supports:
        - website filtering
        - writer filtering
        - status filtering
        - reward rule filtering
        - date filtering
    """

    serializer_class = (
        WriterRewardSerializer
    )

    permission_classes = [
        IsRewardViewer,
    ]

    pagination_class = (
        RewardPagination
    )

    filterset_class = (
        WriterRewardFilter
    )

    ordering_fields = [
        "issued_at",
        "reward_amount",
        "trust_score",
        "percentile_rank",
    ]

    ordering = [
        "-issued_at",
    ]

    def get_queryset( # type: ignore[override]
        self,
    ) -> QuerySet[WriterReward]:
        """
        Return optimized reward queryset.
        """
        request = cast(Request, self.request)
        website_id = (
            request.query_params.get(
                "website_id",
            )
        )

        request = cast(Request, self.request)
        writer_id = (
            request.query_params.get(
                "writer_id",
            )
        )

        
        queryset = (
            RewardAPISelectors.reward_queryset()
        )

        if website_id:
            queryset = queryset.filter(
                website_id=website_id,
            )

        if writer_id:
            queryset = queryset.filter(
                writer_id=writer_id,
            )

        return queryset


class WriterRewardDetailView(
    RetrieveAPIView,
):
    """
    Retrieve immutable reward record.
    """

    serializer_class = (
        WriterRewardSerializer
    )

    permission_classes = [
        IsRewardViewer,
    ]

    lookup_field = "pk"

    queryset = (
        RewardAPISelectors
        .reward_queryset()
    )