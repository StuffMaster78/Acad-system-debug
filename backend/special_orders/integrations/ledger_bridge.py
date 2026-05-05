from __future__ import annotations

from decimal import Decimal
from typing import Any

from ledger.constants import EntrySide
from ledger.models.ledger_account import LedgerAccount
from ledger.services.journal_posting_service import (
    JournalLineInput,
    JournalPostingService,
)
from special_orders.models import SpecialOrder


class SpecialOrderLedgerBridge:
    """
    Optional ledger bridge for special-order-only accounting events.

    Do not use this for external captures if payments_processor already
    posts capture entries.
    Do not use this for wallet debits if wallets already posts wallet
    entries.
    """

    @classmethod
    def post_admin_funding_adjustment(
        cls,
        *,
        special_order: SpecialOrder,
        amount: Decimal,
        debit_account: LedgerAccount,
        credit_account: LedgerAccount,
        reference: str,
        reason: str,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Post manual admin funding adjustment.

        Use only for approved non-provider, non-wallet adjustments.
        """
        return JournalPostingService.post_entry(
            website=special_order.website,
            entry_type="special_order_admin_adjustment",
            currency=special_order.currency,
            description=reason,
            reference=reference,
            source_app="special_orders",
            source_model="SpecialOrder",
            source_object_id=str(special_order.id),
            triggered_by=triggered_by,
            metadata={
                "special_order_id": special_order.id,
                "reason": reason,
                **(metadata or {}),
            },
            lines=[
                JournalLineInput(
                    ledger_account=debit_account,
                    entry_side=EntrySide.DEBIT,
                    amount=amount,
                    description=reason,
                    related_object_type="special_order",
                    related_object_id=str(special_order.id),
                    metadata=metadata or {},
                ),
                JournalLineInput(
                    ledger_account=credit_account,
                    entry_side=EntrySide.CREDIT,
                    amount=amount,
                    description=reason,
                    related_object_type="special_order",
                    related_object_id=str(special_order.id),
                    metadata=metadata or {},
                ),
            ],
        )