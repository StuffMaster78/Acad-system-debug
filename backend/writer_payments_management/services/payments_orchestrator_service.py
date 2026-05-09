from __future__ import annotations

from decimal import Decimal
from django.db import transaction

from writer_payments_management.services.settlement_engine_service import SettlementEngineService
from writer_payments_management.services.exposure_materialization_service import ExposureMaterializationService
from writer_payments_management.services.payout_engine_service import PayoutEngineService
from writer_payments_management.services.reconciliation_service import ReconciliationService
from writer_payments_management.services.outbox_service import OutboxService
from writer_payments_management.factories.correction_event_factory import CorrectionEventFactory


class PaymentsOrchestratorService:
    """
    Single control plane for all payment flows.

    This is NOT business logic.
    This is workflow coordination only.
    """

    # -----------------------------
    # SETTLEMENT FLOW
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def run_settlement(*, website, writer, payment_window):
        period = SettlementEngineService.create_settlement_period(
            website=website,
            writer=writer,
            payment_window=payment_window,
        )

        SettlementEngineService.build_settlement_snapshot(period=period)
        SettlementEngineService.finalize_settlement_period(period=period)

        return period

    # -----------------------------
    # EXPOSURE FLOW
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def materialize_exposure(*, settlement_period):
        ledger = ExposureMaterializationService.materialize_from_settlement(
            period=settlement_period
        )

        return ledger

    # -----------------------------
    # CORRECTION FLOW
    # -----------------------------
    @staticmethod
    def create_correction(*, website, writer, amount, reason, source):
        return CorrectionEventFactory.create(
            website=website,
            writer=writer,
            amount=amount,
            reason=reason,
            correction_type="SYSTEM_CORRECTION",
            source=source,
        )

    # -----------------------------
    # PAYOUT FLOW
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def create_payout_batch(*, website, processed_by=None):
        return PayoutEngineService.create_batch(
            website=website,
            processed_by=processed_by,
        )

    @staticmethod
    @transaction.atomic
    def add_payout_record(*, batch, writer_wallet, amount):
        return PayoutEngineService.add_record(
            batch=batch,
            writer_wallet=writer_wallet,
            amount=amount,
        )

    # -----------------------------
    # RECONCILIATION FLOW
    # -----------------------------
    @staticmethod
    def run_reconciliation(*, website, batch, ledger_total, payout_total, cleared_total):
        report = ReconciliationService.create_report(
            website=website,
            batch=batch,
            ledger_total=ledger_total,
            payout_total=payout_total,
            cleared_total=cleared_total,
        )

        # emit correction if mismatch detected
        if report.mismatch_amount != Decimal("0.00"):
            OutboxService.emit(
                event_type="RECONCILIATION_MISMATCH",
                payload={
                    "batch_id": batch.id,
                    "mismatch": str(report.mismatch_amount),
                },
            )

        return report

    # -----------------------------
    # WALLET SAFETY CHECK
    # -----------------------------
    @staticmethod
    def get_wallet_balance(*, wallet):
        return wallet.available_balance