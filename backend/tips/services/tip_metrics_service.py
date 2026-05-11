from __future__ import annotations

from decimal import Decimal

from tips.services.metrics.tip_platform_metrics_service import (
    TipPlatformMetricsService,
)
from tips.services.metrics.tip_user_metrics_service import (
    TipUserMetricsService,
)
from tips.services.metrics.tip_time_series_metrics_service import (
    TipTimeSeriesMetricsService,
)


class TipMetricsService:
    """
    Central metrics facade for tips.

    DESIGN RULES:
    - No DB queries inside this class
    - Only delegates to domain metric services
    - Safe for API + admin dashboards + analytics layer
    """

    # ------------------------------------------------------------ #
    # PLATFORM METRICS
    # ------------------------------------------------------------ #

    @staticmethod
    def get_platform_volume() -> Decimal:
        return TipPlatformMetricsService.volume()

    @staticmethod
    def get_platform_tip_count() -> int:
        return TipPlatformMetricsService.tip_count()

    @staticmethod
    def get_platform_success_rate() -> Decimal:
        return TipPlatformMetricsService.success_rate()

    @staticmethod
    def get_platform_failure_rate() -> Decimal:
        return TipPlatformMetricsService.failure_rate()

    # ------------------------------------------------------------ #
    # USER METRICS
    # ------------------------------------------------------------ #

    @staticmethod
    def get_user_sent_volume(*, user_id: int) -> Decimal:
        return TipUserMetricsService.sent_volume(user_id=user_id)

    @staticmethod
    def get_user_received_volume(*, user_id: int) -> Decimal:
        return TipUserMetricsService.received_volume(user_id=user_id)

    @staticmethod
    def get_user_tip_count(*, user_id: int) -> int:
        return TipUserMetricsService.sent_count(user_id=user_id)

    # ------------------------------------------------------------ #
    # TIME SERIES METRICS
    # ------------------------------------------------------------ #

    @staticmethod
    def get_volume_last_24h() -> Decimal:
        return TipTimeSeriesMetricsService.volume_last_24h()

    @staticmethod
    def get_volume_last_7_days() -> Decimal:
        return TipTimeSeriesMetricsService.volume_last_7_days()

    # ------------------------------------------------------------ #
    # FINANCIAL BREAKDOWN METRICS
    # ------------------------------------------------------------ #

    @staticmethod
    def get_writer_earnings_total() -> Decimal:
        """
        Total writer earnings (system-wide).
        """
        from django.db.models import Sum
        from tips.models.tip import Tip
        from tips.enums.tip_status import TipStatus

        return (
            Tip.objects.filter(status=TipStatus.SUCCEEDED)
            .aggregate(total=Sum("writer_share_cents"))
            .get("total")
            or Decimal("0")
        )

    @staticmethod
    def get_platform_fees_total() -> Decimal:
        """
        Total platform revenue from tips.
        """
        from django.db.models import Sum
        from tips.models.tip import Tip
        from tips.enums.tip_status import TipStatus

        return (
            Tip.objects.filter(status=TipStatus.SUCCEEDED)
            .aggregate(total=Sum("platform_fee_cents"))
            .get("total")
            or Decimal("0")
        )