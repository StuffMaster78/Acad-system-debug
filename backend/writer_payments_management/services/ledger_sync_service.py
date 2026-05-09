from __future__ import annotations

from decimal import Decimal
from typing import Any


class LedgerSyncService:
    """
    Pure comparison layer between Wallet and ExposureLedger.

    RULES:
        1. No mutations
        2. No calculations beyond delta
        3. No domain knowledge (no financial logic here)
        4. Safe for monitoring, alerts, and reconciliation triggers
    """

    @staticmethod
    def compare(
        *,
        wallet: Any,
        ledger: Any,
    ) -> dict[str, Any]:
        """
        Compare wallet state vs exposure ledger state.

        Returns a deterministic diff snapshot.
        """

        if wallet is None or ledger is None:
            raise ValueError("wallet and ledger must not be None")

        # -----------------------------
        # SAFETY: ensure numeric coercion stability
        # -----------------------------
        expected = Decimal(str(ledger.recoverable_balance or "0.00"))
        actual = Decimal(str(wallet.available_balance or "0.00"))

        difference = expected - actual

        return {
            "wallet_id": getattr(wallet, "id", None),
            "ledger_id": getattr(ledger, "id", None),
            "expected": expected,
            "actual": actual,
            "difference": difference,
            "in_sync": difference == Decimal("0.00"),
        }