from __future__ import annotations

from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

from tips.models.tip import Tip
from tips.enums.tip_status import TipStatus


class TipTimeSeriesMetricsService:

    @staticmethod
    def volume_last_24h() -> Decimal:
        since = timezone.now() - timedelta(hours=24)

        return (
            Tip.objects
            .filter(status=TipStatus.SUCCEEDED, created_at__gte=since)
            .aggregate(total=Sum("gross_amount"))
            .get("total")
            or Decimal("0")
        )

    @staticmethod
    def volume_last_7_days() -> Decimal:
        since = timezone.now() - timedelta(days=7)

        return (
            Tip.objects
            .filter(status=TipStatus.SUCCEEDED, created_at__gte=since)
            .aggregate(total=Sum("gross_amount"))
            .get("total")
            or Decimal("0")
        )