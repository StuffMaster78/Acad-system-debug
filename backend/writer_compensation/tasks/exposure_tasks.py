from __future__ import annotations

from celery import shared_task
from django.db import transaction

from writer_compensation.models.settlement_period import SettlementPeriod
from writer_compensation.services.exposure_materialization_service import (
    ExposureMaterializationService,
)
from writer_compensation.services.ledger_sync_service import LedgerSyncService
from writer_compensation.services.risk_engine_service import RiskEngineService
from writer_compensation.factories.correction_event_factory import (
    CorrectionEventFactory,
)
from wallets.services.writer_wallet_service import WriterWalletService


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
        wallet = WriterWalletService.get_wallet(
            website=period.website,
            writer=_writer_user(period.writer),
        )

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


def _writer_user(writer_profile):
    return getattr(writer_profile, "user", None) or writer_profile.account_profile.user
