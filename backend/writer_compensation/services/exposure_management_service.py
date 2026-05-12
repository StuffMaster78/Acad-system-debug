from __future__ import annotations

from decimal import Decimal
from writer_compensation.models.exposure_ledger import ExposureLedger


class ExposureManagementService:
    """
    Risk engine layer.

    RULE:
        NEVER recompute financial truth.
        ONLY interpret ExposureLedger.
    """

    @staticmethod
    def get_available_balance(*, ledger: ExposureLedger) -> Decimal:

        max_exposure = (
            ledger.total_earned
            * ledger.risk_cap_percentage
            / Decimal("100")
        )

        return max(
            Decimal("0.00"),
            max_exposure - ledger.total_advance_taken,
        )

    @staticmethod
    def can_withdraw_advance(
        *,
        ledger: ExposureLedger,
        requested_amount: Decimal,
    ) -> bool:

        return requested_amount <= ExposureManagementService.get_available_balance(
            ledger=ledger
        )

    @staticmethod
    def apply_advance(
        *,
        ledger: ExposureLedger,
        amount: Decimal,
    ) -> ExposureLedger:

        ledger.total_advance_taken += amount
        ledger.save(update_fields=["total_advance_taken"])

        return ledger

    @staticmethod
    def apply_payout(
        *,
        ledger: ExposureLedger,
        amount: Decimal,
    ) -> ExposureLedger:

        ledger.total_paid += amount
        ledger.save(update_fields=["total_paid"])

        return ledger