from __future__ import annotations

from django.db.models import QuerySet

from ledger.models.reconciliation_record import ReconciliationRecord
from ledger.constants import ReconciliationStatus

class ReconciliationSelectors:
    """
    Read only queries for reconciliation records.
    """

    @staticmethod
    def get_records_for_website(*, website) -> QuerySet[ReconciliationRecord]:
        return ReconciliationRecord.objects.filter(
            website=website
        ).order_by("-created_at")

    @staticmethod
    def get_record_by_id(
        *,
        website,
        record_id,
    ) -> ReconciliationRecord:
        return ReconciliationRecord.objects.get(
            website=website,
            id=record_id,
        )

    @staticmethod
    def get_records_by_status(
        *,
        website,
        status: str,
    ) -> QuerySet[ReconciliationRecord]:
        return ReconciliationRecord.objects.filter(
            website=website,
            status=status,
        ).order_by("-created_at")

    @staticmethod
    def get_records_by_reference(
        *,
        website,
        reference: str,
    ) -> QuerySet[ReconciliationRecord]:
        return ReconciliationRecord.objects.filter(
            website=website,
            reference=reference,
        ).order_by("-created_at")

    @staticmethod
    def get_records_by_external_reference(
        *,
        website,
        external_reference: str,
    ) -> QuerySet[ReconciliationRecord]:
        return ReconciliationRecord.objects.filter(
            website=website,
            external_reference=external_reference,
        ).order_by("-created_at")

    @staticmethod
    def get_records_for_source_object(
        *,
        website,
        source_model: str,
        source_object_id: str,
    ) -> QuerySet[ReconciliationRecord]:
        return ReconciliationRecord.objects.filter(
            website=website,
            source_model=source_model,
            source_object_id=source_object_id,
        ).order_by("-created_at")

    @staticmethod
    def get_unresolved_records(*, website) -> QuerySet[ReconciliationRecord]:
        return ReconciliationRecord.objects.exclude(
            status=ReconciliationStatus.RESOLVED
        ).filter(
            website=website
        ).order_by("-created_at")