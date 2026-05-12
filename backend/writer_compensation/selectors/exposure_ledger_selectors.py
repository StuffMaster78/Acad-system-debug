from __future__ import annotations

from django.db.models import QuerySet

from writer_compensation.models.exposure_ledger import ExposureLedger


class ExposureLedgerSelectors:
    """
    Read-only exposure ledger access layer.
    """

    @staticmethod
    def base_queryset() -> QuerySet:
        return ExposureLedger.objects.select_related(
            "website",
            "writer",
        )

    @staticmethod
    def by_writer(*, website, writer) -> QuerySet:
        return ExposureLedgerSelectors.base_queryset().filter(
            website=website,
            writer=writer,
        )

    @staticmethod
    def for_update(*, ledger_id: int) -> ExposureLedger:
        return ExposureLedger.objects.select_for_update().get(
            id=ledger_id
        )