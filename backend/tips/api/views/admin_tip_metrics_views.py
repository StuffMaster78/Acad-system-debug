# tips/api/views/admin_tip_metrics_views.py

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from tips.services.tip_metrics_service import (
    TipMetricsService,
)


class AdminPlatformAnalyticsAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        data = {
            "platform_volume": (
                TipMetricsService.get_platform_volume()
            ),
            "platform_tip_count": (
                TipMetricsService.get_platform_tip_count()
            ),
            "success_rate": (
                TipMetricsService.get_platform_success_rate()
            ),
            "failure_rate": (
                TipMetricsService.get_failure_rate()
            ),
            "platform_fees_total": (
                TipMetricsService.get_platform_fees_total()
            ),
            "pending_tips": (
                TipMetricsService.get_pending_tips_count()
            ),
        }

        return Response(data)


class AdminTopTippersAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        data = (
            TipMetricsService.get_top_tippers()
        )

        return Response(data)


class AdminTopWritersAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        data = (
            TipMetricsService.get_top_writers()
        )

        return Response(data)


class AdminTipTimeseriesAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        data = (
            TipMetricsService
            .get_last_7_days_volume()
        )

        return Response(data)