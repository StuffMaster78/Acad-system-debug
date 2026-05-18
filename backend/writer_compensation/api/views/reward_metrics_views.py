from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.services.reward_analytics_service import (
    RewardAnalyticsService,
)


class RewardMetricsView(
    APIView,
):
    """
    Reward metrics dashboard endpoint.
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
        Return reward metrics.
        """

        website_id = (
            request.query_params.get(
                "website_id",
            )
        )

        metrics = (
            RewardAnalyticsService.website_metrics(
                website_id=website_id,
            )
        )

        return Response(
            metrics,
        )