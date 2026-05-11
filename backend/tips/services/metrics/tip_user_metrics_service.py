from __future__ import annotations

from decimal import Decimal
from django.db.models import Sum, Count

from tips.models.tip import Tip
from tips.enums.tip_status import TipStatus


class TipUserMetricsService:

    @staticmethod
    def sent_volume(*, user_id: int) -> Decimal:
        return (
            Tip.objects
            .filter(sender_id=user_id, status=TipStatus.SUCCEEDED)
            .aggregate(total=Sum("gross_amount"))
            .get("total")
            or Decimal("0")
        )

    @staticmethod
    def received_volume(*, user_id: int) -> Decimal:
        return (
            Tip.objects
            .filter(receiver_id=user_id, status=TipStatus.SUCCEEDED)
            .aggregate(total=Sum("gross_amount"))
            .get("total")
            or Decimal("0")
        )

    @staticmethod
    def sent_count(*, user_id: int) -> int:
        return (
            Tip.objects
            .filter(sender_id=user_id, status=TipStatus.SUCCEEDED)
            .count()
        )