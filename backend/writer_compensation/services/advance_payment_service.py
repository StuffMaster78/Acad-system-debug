from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from writer_compensation.models.exposure_ledger import (
    ExposureLedger,
)

from writer_compensation.services.risk_engine_service import (
    RiskEngineService,
)


class AdvancePaymentService:
    """
    Handles writer advance eligibility and exposure updates.

    Core financial rule:
        Advances are liabilities against future earnings.

    Meaning:
        - increase total advance exposure
        - reduce recoverable balance
        - never mutate historical earnings
    """

    @staticmethod
    def can_request(
        *,
        ledger: ExposureLedger,
        amount: Decimal,
    ) -> bool:
        """
        Determine whether writer can request an advance.

        Validation rules:
            1. amount must be positive
            2. writer must have remaining risk capacity
        """

        if amount <= Decimal("0.00"):
            return False

        return RiskEngineService.can_issue_advance(
            ledger=ledger,
            amount=amount,
        )

    @staticmethod
    @transaction.atomic
    def apply_advance(
        *,
        ledger: ExposureLedger,
        amount: Decimal,
    ) -> ExposureLedger:
        """
        Apply advance exposure safely.

        Effects:
            - increases advance exposure
            - decreases recoverable balance
        """

        if amount <= Decimal("0.00"):
            raise ValueError(
                "Advance amount must be greater than zero."
            )

        if not AdvancePaymentService.can_request(
            ledger=ledger,
            amount=amount,
        ):
            raise ValueError(
                "Advance exceeds allowed exposure capacity."
            )

        ledger.total_advance_taken += amount

        ledger.recoverable_balance -= amount

        ledger.save(
            update_fields=[
                "total_advance_taken",
                "recoverable_balance",
                "last_updated",
            ],
        )

        return ledger
