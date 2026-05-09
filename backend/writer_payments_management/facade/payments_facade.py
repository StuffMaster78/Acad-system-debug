from __future__ import annotations

from decimal import Decimal
from typing import Any

from writer_payments_management.factories.correction_event_factory import CorrectionEventFactory
from writer_payments_management.services.settlement_engine_service import SettlementEngineService
from writer_payments_management.services.settlement_validation_layer import SettlementValidationService
from writer_payments_management.services.risk_engine_service import RiskEngineService
from writer_payments_management.exceptions import ExposureLimitBreachedError


class PaymentsFacade:

    @staticmethod
    def create_correction_event(
        *,
        website: Any,
        writer: Any,
        amount: Decimal,
        reason: str,
        source: str,
        created_by: Any | None = None,
        idempotency_key: str | None = None,
    ):
        PaymentsFacade._validate_amount(amount)

        return CorrectionEventFactory.create(
            website=website,
            writer=writer,
            amount=amount,
            reason=reason,
            correction_type="SYSTEM_CORRECTION",
            source=source,
            created_by=created_by,
            idempotency_key=idempotency_key,
        )

    @staticmethod
    def run_settlement(
        *,
        website: Any,
        writer: Any,
        payment_window: Any,
        auto_finalize: bool = True,
    ):
        period = SettlementEngineService.create_settlement_period(
            website=website,
            writer=writer,
            payment_window=payment_window,
        )

        SettlementEngineService.build_settlement_snapshot(period=period)

        SettlementValidationService.assert_valid(period=period)

        SettlementEngineService.create_settlement_items(period=period)

        if auto_finalize:
            SettlementEngineService.finalize_settlement_period(period=period)

        return period

    @staticmethod
    def get_wallet_balance(*, wallet: Any):
        return wallet.available_balance

    @staticmethod
    def can_issue_advance(*, ledger: Any, amount: Decimal) -> bool:
        return RiskEngineService.can_issue_advance(
            ledger=ledger,
            amount=amount,
        )

    @staticmethod
    def _validate_amount(amount: Decimal) -> None:
        if not isinstance(amount, Decimal):
            raise TypeError("amount must be Decimal")

        if amount <= Decimal("0.00"):
            raise ValueError("amount must be greater than zero")