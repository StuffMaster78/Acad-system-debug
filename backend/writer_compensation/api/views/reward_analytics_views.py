# writer_compensation/api/views/reward_analytics_views.py

from __future__ import annotations

from decimal import Decimal

from django.db.models import Avg
from django.db.models import Count
from django.db.models import Sum

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.models.writer_reward import (
    WriterReward,
)
from writer_compensation.services.reward_analytics_service import (
    RewardAnalyticsService,
)


class RewardAnalyticsOverviewView(
    APIView,
):
    """
    Aggregate reward analytics endpoint.
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
        Return reward analytics overview.
        """

        website_id = (
            request.query_params.get(
                "website_id",
            )
        )

        payload = (
            RewardAnalyticsService
            .overview_metrics(
                website_id=website_id,
            )
        )

        return Response(
            payload,
        )

class RewardAnalyticsView(
    APIView,
):
    """
    Reward analytics endpoint.

    Powers:
        - admin dashboards
        - finance visibility
        - incentive analysis
        - retention intelligence
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
        Return aggregate reward analytics.
        """

        queryset = (
            WriterReward.objects
            .select_related(
                "writer",
                "reward_rule",
                "website",
            )
        )

        website_id = request.query_params.get(
            "website_id",
        )

        if website_id:
            queryset = queryset.filter(
                website_id=website_id,
            )

        total_rewards = queryset.count()

        total_reward_amount = (
            queryset.aggregate(
                total=Sum(
                    "reward_amount",
                )
            )["total"]
            or Decimal("0.00")
        )

        average_reward_amount = (
            queryset.aggregate(
                avg=Avg(
                    "reward_amount",
                )
            )["avg"]
            or Decimal("0.00")
        )

        issued_rewards = queryset.filter(
            status=(
                WriterReward
                .RewardStatus
                .ISSUED
            )
        ).count()

        revoked_rewards = queryset.filter(
            status=(
                WriterReward
                .RewardStatus
                .REVOKED
            )
        ).count()

        top_reward_rules = list(
            queryset.values(
                "reward_rule__name",
            )
            .annotate(
                total=Count(
                    "id",
                )
            )
            .order_by(
                "-total",
            )[:10]
        )

        top_writers = list(
            queryset.values(
                "writer__id",
                "writer__display_name",
            )
            .annotate(
                total_rewards=Count(
                    "id",
                ),
                total_amount=Sum(
                    "reward_amount",
                ),
            )
            .order_by(
                "-total_amount",
            )[:10]
        )

        payload = {
            "total_rewards": (
                total_rewards
            ),
            "issued_rewards": (
                issued_rewards
            ),
            "revoked_rewards": (
                revoked_rewards
            ),
            "total_reward_amount": str(
                total_reward_amount,
            ),
            "average_reward_amount": str(
                average_reward_amount,
            ),
            "top_reward_rules": (
                top_reward_rules
            ),
            "top_writers": (
                top_writers
            ),
        }

        return Response(
            payload,
        )