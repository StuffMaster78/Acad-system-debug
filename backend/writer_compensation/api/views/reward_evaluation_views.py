# writer_compensation/api/views/reward_evaluation_views.py

from __future__ import annotations

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.services.reward_evaluation_orchestrator import (
    RewardEvaluationOrchestrator,
)


class RunWeeklyRewardsView(
    APIView,
):
    """
    Manual weekly reward trigger.
    """

    permission_classes = [
        IsAdminUser,
    ]

    def post(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """
        Execute weekly reward cycle.
        """

        RewardEvaluationOrchestrator.run_weekly_rewards()

        return Response(
            {
                "detail": (
                    "Weekly rewards executed."
                ),
            }
        )


class RunMonthlyRewardsView(
    APIView,
):
    """
    Manual monthly reward trigger.
    """

    permission_classes = [
        IsAdminUser,
    ]

    def post(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """
        Execute monthly reward cycle.
        """

        RewardEvaluationOrchestrator.run_monthly_rewards()

        return Response(
            {
                "detail": (
                    "Monthly rewards executed."
                ),
            }
        )