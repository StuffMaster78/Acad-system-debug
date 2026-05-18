# writer_compensation/api/views/reward_admin_views.py

from __future__ import annotations

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_compensation.models.writer_reward import (
    WriterReward,
)
from writer_compensation.services.reward_admin_service import (
    RewardAdminService,
)


class RewardRevocationView(
    APIView,
):
    """
    Administrative reward revocation endpoint.
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
        Revoke reward.
        """

        reward_id = (
            self.kwargs.get(
                "reward_id",
            )
        )

        reason = (
            request.data.get(
                "reason",
                "",
            )
        )

        reward = (
            WriterReward.objects
            .select_related(
                "writer",
                "reward_rule",
            )
            .filter(
                pk=reward_id,
            )
            .first()
        )

        if reward is None:
            return Response(
                {
                    "detail": (
                        "Reward not found."
                    ),
                },
                status=404,
            )

        RewardAdminService.revoke_reward(
            reward=reward,
            revoked_by=request.user,
            reason=reason,
        )

        return Response(
            {
                "detail": (
                    "Reward revoked."
                ),
            }
        )