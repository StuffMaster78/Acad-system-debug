# writer_compensation/api/views/reward_fraud_views.py

from __future__ import annotations


from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.permissions import IsAdminOrSuperAdmin

from writer_compensation.services.reward_fraud_detection_service import (
    RewardFraudDetectionService,
)


class RewardFraudCheckView(
    APIView,
):
    """
    Fraud evaluation endpoint.
    """

    permission_classes = [
        IsAdminOrSuperAdmin,
    ]

    def get(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """
        Evaluate fraud risk for writer.
        """

        writer_id = (
            self.kwargs.get(
                "writer_id",
            )
        )

        result = (
            RewardFraudDetectionService
            .evaluate_writer(
                writer_id=writer_id,
            )
        )

        payload = {
            "is_safe": (
                result.is_safe
            ),
            "risk_score": (
                result.risk_score
            ),
            "flags": (
                result.flags
            ),
        }

        return Response(
            payload,
        )