from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from special_orders.integrations.wallet_adapter import (
    SpecialOrderWalletAdapter,
)
from special_orders.models.special_order import (
    SpecialOrder,
)
from special_orders.models.funding import (
    SpecialOrderFundingMilestone,
)
from special_orders.services.new_services.special_order_payment_orchestration_service import (
    SpecialOrderPaymentOrchestrationService,
)


class SpecialOrderWalletBridge:
    """
    Bridge wallet debits into special order funding.

    wallets owns balances and wallet transactions.
    ledger owns accounting entries.
    special_orders only applies confirmed funding.
    """

    @classmethod
    @transaction.atomic
    def pay_from_wallet(
        cls,
        *,
        special_order: SpecialOrder,
        amount: Decimal,
        milestone: SpecialOrderFundingMilestone | None = None,
        paid_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Debit client wallet, post ledger entry, and apply funds.

        Replace placeholder calls with your actual wallet and ledger services.
        """
        cls._validate_amount(amount=amount)
        cls._validate_milestone(
            special_order=special_order,
            milestone=milestone,
        )

        wallet_result = SpecialOrderWalletAdapter.debit_client_wallet(
            website=special_order.website,
            client=special_order.client,
            amount=amount,
            special_order=special_order,
            currency=special_order.currency,
            milestone=milestone,
            triggered_by=paid_by,
            metadata={
                "source_app": "special_orders",
                "special_order_id": special_order.id,
                "milestone_id": milestone.id if milestone else None,
                **(metadata or {}),
            },
        )

        idempotency_key = (
            "wallet:"
            f"special_order:"
            f"{wallet_result.wallet_transaction_reference}"
        )

        return SpecialOrderPaymentOrchestrationService.apply_wallet_payment(
            special_order=special_order,
            amount=wallet_result.amount,
            idempotency_key=(
                "wallet:"
                f"special_order:"
                f"{wallet_result.wallet_transaction_reference}"
            ),
            wallet_transaction_reference=(
                wallet_result.wallet_transaction_reference
            ),
            ledger_entry_reference=wallet_result.ledger_entry_reference,
            milestone=milestone,
            applied_by=paid_by,
            metadata={
                "source": "wallet_bridge",
                **wallet_result.metadata,
            },
        )

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        if amount <= Decimal("0.00"):
            raise ValueError("Wallet payment amount must be greater than zero.")

    @staticmethod
    def _validate_milestone(
        *,
        special_order: SpecialOrder,
        milestone: SpecialOrderFundingMilestone | None,
    ) -> None:
        if milestone is None:
            return

        if milestone.website_id != special_order.website_id:
            raise ValueError("Milestone belongs to another tenant.")

        if milestone.special_order_id != special_order.id:
            raise ValueError("Milestone belongs to another special order.")

    @staticmethod
    def _build_wallet_reference(
        *,
        special_order: SpecialOrder,
        milestone: SpecialOrderFundingMilestone | None,
    ) -> str:
        milestone_part = milestone.id if milestone else "plan"
        return f"wallet:special_order:{special_order.id}:{milestone_part}"

    @staticmethod
    def _build_ledger_reference(
        *,
        special_order: SpecialOrder,
        milestone: SpecialOrderFundingMilestone | None,
    ) -> str:
        milestone_part = milestone.id if milestone else "plan"
        return f"ledger:special_order_wallet:{special_order.id}:{milestone_part}"

    @staticmethod
    def _build_idempotency_key(
        *,
        special_order: SpecialOrder,
        amount: Decimal,
        wallet_transaction_reference: str,
    ) -> str:
        return (
            "wallet:"
            f"special_order:{special_order.id}:"
            f"{wallet_transaction_reference}:"
            f"{amount}"
        )