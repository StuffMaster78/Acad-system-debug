# writer_compensation/api/views/reward_orchestration_views.py

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.services.reward_evaluation_orchestrator import (
    RewardEvaluationOrchestrator,
)


class RunWeeklyRewardsView(
    APIView,
):
    """
    Execute weekly reward cycle.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """
        Run weekly rewards.
        """

        RewardEvaluationOrchestrator.run_weekly_rewards()

        return Response(
            {
                "detail": (
                    "Weekly reward evaluation started."
                ),
            },
            status=status.HTTP_202_ACCEPTED,
        )


class RunMonthlyRewardsView(
    APIView,
):
    """
    Execute monthly reward cycle.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """
        Run monthly rewards.
        """

        RewardEvaluationOrchestrator.run_monthly_rewards()

        return Response(
            {
                "detail": (
                    "Monthly reward evaluation started."
                ),
            },
            status=status.HTTP_202_ACCEPTED,
        )