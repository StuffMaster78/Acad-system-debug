from __future__ import annotations

from django.db.models import QuerySet

from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.enums.financial_event_enums import (
    FinancialEventStatus,
)


class FinancialEventSelectors:
    """
    Read-only query layer for FinancialEvent.

    RULE:
        No aggregation logic beyond filters.
        No business computation.
    """

    @staticmethod
    def base_queryset() -> QuerySet:
        return CompensationEvent.objects.select_related(
            "website",
            "writer",
            "settlement_period",
        )

    @staticmethod
    def by_writer(*, website, writer) -> QuerySet:
        return FinancialEventSelectors.base_queryset().filter(
            website=website,
            writer=writer,
        )

    @staticmethod
    def matured_unsettled(*, website, writer) -> QuerySet:
        return FinancialEventSelectors.by_writer(
            website=website,
            writer=writer,
        ).filter(
            status=FinancialEventStatus.MATURED,
            settlement_period__isnull=True,
        )

    @staticmethod
    def by_settlement_period(*, period) -> QuerySet:
        return FinancialEventSelectors.base_queryset().filter(
            website=period.website,
            writer=period.writer,
            created_at__range=(
                period.payment_window.start_date,
                period.payment_window.end_date,
            ),
        )