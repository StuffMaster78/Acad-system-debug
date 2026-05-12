from __future__ import annotations

from django.db.models import QuerySet

from writer_compensation.models.settlement_period import SettlementPeriod
from writer_compensation.enums.financial_event_enums import (
    SettlementStatus,
)


class SettlementSelectors:
    """
    Read-only settlement access layer.
    """

    @staticmethod
    def base_queryset() -> QuerySet:
        return SettlementPeriod.objects.select_related(
            "website",
            "writer",
            "payment_window",
        )

    @staticmethod
    def active_periods(*, website) -> QuerySet:
        return SettlementSelectors.base_queryset().filter(
            website=website,
            status=SettlementStatus.OPEN,
        )

    @staticmethod
    def by_writer(*, website, writer) -> QuerySet:
        return SettlementSelectors.base_queryset().filter(
            website=website,
            writer=writer,
        )

    @staticmethod
    def locked_periods(*, website) -> QuerySet:
        return SettlementSelectors.base_queryset().filter(
            website=website,
            status=SettlementStatus.LOCKED,
        )