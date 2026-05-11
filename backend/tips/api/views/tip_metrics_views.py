# tips/api/views/tip_metrics_views.py

from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tips.services.tip_metrics_service import (
    TipMetricsService,
)


class PlatformTipMetricsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        data = {
            "platform_volume": (
                TipMetricsService.get_platform_volume()
            ),
            "platform_tip_count": (
                TipMetricsService.get_platform_tip_count()
            ),
            "platform_success_rate": (
                TipMetricsService.get_platform_success_rate()
            ),
            "platform_fees_total": (
                TipMetricsService.get_platform_fees_total()
            ),
            # "failure_rate": (
            #     TipMetricsService.get_failure_rate()
            # ),
            # "pending_tips_count": (
            #     TipMetricsService.get_pending_tips_count()
            # ),
        }

        return Response(data)


class UserTipMetricsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_id = request.user.pk

        data = {
            "sent_volume": (
                TipMetricsService.get_user_sent_volume(
                    user_id=user_id,
                )
            ),
            "received_volume": (
                TipMetricsService.get_user_received_volume(
                    user_id=user_id,
                )
            ),
            "tip_count": (
                TipMetricsService.get_user_tip_count(
                    user_id=user_id,
                )
            ),
        }

        return Response(data)