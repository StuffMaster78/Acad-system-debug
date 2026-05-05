from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, cast

from django.db import transaction

from wallets.constants import WalletEntryType, WalletType
from wallets.services.wallet_ledger_integration_service import (
    WalletLedgerIntegrationService,
)
from wallets.services.wallet_service import WalletService


@dataclass(frozen=True)
class WalletDebitResult:
    wallet_transaction_reference: str
    ledger_entry_reference: str
    amount: Decimal
    currency: str
    metadata: dict[str, Any]


class SpecialOrderWalletAdapter:
    """
    Adapter between wallets and special_orders.
    """

    @staticmethod
    @transaction.atomic
    def debit_client_wallet(
        *,
        website,
        client,
        amount: Decimal,
        currency: str,
        special_order,
        milestone=None,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> WalletDebitResult:
        wallet = WalletService.get_wallet_by_owner_and_type(
            website=website,
            owner_user=client,
            wallet_type=WalletType.CLIENT,
            currency=currency,
        )

        reference = f"special_order_wallet:{special_order.id}"
        reference_id = str(special_order.id)

        wallet_entry = WalletService.debit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=WalletEntryType.ORDER_PAYMENT,
            website=website,
            created_by=triggered_by,
            description="Wallet payment applied to special order",
            reference=reference,
            reference_type="special_order",
            reference_id=reference_id,
            metadata={
                "special_order_id": special_order.id,
                "milestone_id": milestone.id if milestone else None,
                **(metadata or {}),
            },
        )

        journal_entry = (
            WalletLedgerIntegrationService.post_wallet_order_payment(
                website=website,
                wallet=wallet,
                amount=amount,
                created_by=triggered_by,
                reference=reference,
                source_object_id=reference_id,
                description="Wallet payment applied to special order",
                metadata={
                    "source_app": "special_orders",
                    "wallet_entry_id": cast(Any, wallet_entry).id,
                    "special_order_id": special_order.id,
                    "milestone_id": milestone.id if milestone else None,
                    **(metadata or {}),
                },
            )
        )

        return WalletDebitResult(
            wallet_transaction_reference=str(cast(Any, wallet_entry).id),
            ledger_entry_reference=str(cast(Any, journal_entry).id),
            amount=amount,
            currency=currency,
            metadata={
                "wallet_entry_id": cast(Any, wallet_entry).id,
                "journal_entry_id": cast(Any, journal_entry).id,
            },
        )