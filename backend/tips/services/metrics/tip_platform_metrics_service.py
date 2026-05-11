from __future__ import annotations

from decimal import Decimal
from django.db.models import Sum, Count

from tips.models.tip import Tip
from tips.enums.tip_status import TipStatus


class TipPlatformMetricsService:

    @staticmethod
    def volume() -> Decimal:
        return (
            Tip.objects
            .filter(status=TipStatus.SUCCEEDED)
            .aggregate(total=Sum("gross_amount"))
            .get("total")
            or Decimal("0")
        )

    @staticmethod
    def tip_count() -> int:
        return (
            Tip.objects
            .filter(status=TipStatus.SUCCEEDED)
            .aggregate(total=Count("id"))
            .get("total")
            or 0
        )

    @staticmethod
    def success_rate() -> Decimal:
        total = Tip.objects.count()
        success = Tip.objects.filter(status=TipStatus.SUCCEEDED).count()

        if total == 0:
            return Decimal("0")

        return Decimal(success / total).quantize(Decimal("0.01"))

    @staticmethod
    def failure_rate() -> Decimal:
        total = Tip.objects.count()
        failed = Tip.objects.filter(status=TipStatus.FAILED).count()

        if total == 0:
            return Decimal("0")

        return Decimal(failed / total).quantize(Decimal("0.01"))