from __future__ import annotations

from celery import shared_task
from django.db import transaction

from writer_payments_management.models.settlement_period_models import SettlementPeriod
from writer_payments_management.services.exposure_materialization_service import (
    ExposureMaterializationService,
)
from writer_payments_management.services.ledger_sync_service import LedgerSyncService
from writer_payments_management.services.risk_engine_service import RiskEngineService
from writer_payments_management.factories.correction_event_factory import (
    CorrectionEventFactory,
)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def materialize_exposure_from_settlement(self, settlement_period_id: int):
    """
    Entry point for exposure pipeline.

    Safe to retry:
        - idempotent updates
        - delta-safe ledger updates
    """

    with transaction.atomic():
        period = SettlementPeriod.objects.select_related("website", "writer").get(
            id=settlement_period_id
        )

        # 1. Materialize exposure from settlement snapshot
        ledger = ExposureMaterializationService.materialize_from_settlement(
            period=period
        )

        # 2. Sync check (wallet vs ledger drift detection)
        # NOTE: wallet lookup should be injected later via wallet service
        # Keeping soft coupling for now
        wallet = getattr(period.writer, "wallet", None)

        if wallet:
            diff_report = LedgerSyncService.compare(
                wallet=wallet,
                ledger=ledger,
            )

            # 3. If drift exists → emit correction event
            if not diff_report["in_sync"]:
                CorrectionEventFactory.create(
                    website=period.website,
                    writer=period.writer,
                    amount=diff_report["difference"],
                    reason="Auto reconciliation drift detected from settlement",
                    correction_type="SETTLEMENT_MISMATCH",
                    source="EXPOSURE_TASK",
                )

        # 4. Risk refresh (light recompute trigger)
        # (no persistence unless needed later)
        RiskEngineService.get_available_risk_capacity(ledger=ledger)

        return {
            "ledger_id": ledger.pk,
            "settlement_period_id": period.pk,
            "status": "EXPOSURE_MATERIALIZED",
        }