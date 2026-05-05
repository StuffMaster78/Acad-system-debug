from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from special_orders.constants import PaymentApplicationSource
from special_orders.models import (
    SpecialOrder,
    SpecialOrderFundingMilestone,
)
from special_orders.services.new_services.special_order_payment_application_service import (
    SpecialOrderPaymentApplicationService,
)


class SpecialOrderPaymentOrchestrationService:
    """
    Coordinates special order funding from wallet, external payments,
    admin adjustments, and split payment flows.

    This service should call wallet, payments_processor, and ledger services.
    The final local funding write is delegated to
    SpecialOrderPaymentApplicationService.
    """

    @classmethod
    @transaction.atomic
    def apply_external_payment(
        cls,
        *,
        special_order: SpecialOrder,
        amount: Decimal,
        idempotency_key: str,
        payment_intent_reference: str,
        payment_transaction_reference: str,
        ledger_entry_reference: str,
        milestone: SpecialOrderFundingMilestone | None = None,
        applied_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Apply an already verified external payment.

        Expected caller:
            payments_processor webhook/application service after provider
            verification and ledger posting.
        """
        return SpecialOrderPaymentApplicationService.apply_payment(
            special_order=special_order,
            amount=amount,
            source=PaymentApplicationSource.EXTERNAL,
            idempotency_key=idempotency_key,
            milestone=milestone,
            payment_intent_reference=payment_intent_reference,
            payment_transaction_reference=payment_transaction_reference,
            ledger_entry_reference=ledger_entry_reference,
            applied_by=applied_by,
            metadata=metadata,
        )

    @classmethod
    @transaction.atomic
    def apply_wallet_payment(
        cls,
        *,
        special_order: SpecialOrder,
        amount: Decimal,
        idempotency_key: str,
        wallet_transaction_reference: str,
        ledger_entry_reference: str,
        milestone: SpecialOrderFundingMilestone | None = None,
        applied_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Apply an already debited wallet payment.

        Expected caller:
            wallet orchestration after wallet debit and ledger posting.
        """
        return SpecialOrderPaymentApplicationService.apply_payment(
            special_order=special_order,
            amount=amount,
            source=PaymentApplicationSource.WALLET,
            idempotency_key=idempotency_key,
            milestone=milestone,
            wallet_transaction_reference=wallet_transaction_reference,
            ledger_entry_reference=ledger_entry_reference,
            applied_by=applied_by,
            metadata=metadata,
        )

    @classmethod
    @transaction.atomic
    def apply_admin_adjustment(
        cls,
        *,
        special_order: SpecialOrder,
        amount: Decimal,
        idempotency_key: str,
        ledger_entry_reference: str | None = None,
        milestone: SpecialOrderFundingMilestone | None = None,
        applied_by=None,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
    ):
        """
        Apply an approved admin funding adjustment.

        This should only be called after an admin override has been approved.
        """
        adjustment_metadata = {
            "reason": reason,
            **(metadata or {}),
        }

        return SpecialOrderPaymentApplicationService.apply_payment(
            special_order=special_order,
            amount=amount,
            source=PaymentApplicationSource.ADMIN_ADJUSTMENT,
            idempotency_key=idempotency_key,
            milestone=milestone,
            ledger_entry_reference=ledger_entry_reference,
            applied_by=applied_by,
            metadata=adjustment_metadata,
        )

    @classmethod
    @transaction.atomic
    def apply_split_payment(
        cls,
        *,
        special_order: SpecialOrder,
        wallet_amount: Decimal,
        external_amount: Decimal,
        wallet_idempotency_key: str,
        external_idempotency_key: str,
        wallet_transaction_reference: str,
        payment_intent_reference: str,
        payment_transaction_reference: str,
        wallet_ledger_entry_reference: str,
        external_ledger_entry_reference: str,
        milestone: SpecialOrderFundingMilestone | None = None,
        applied_by=None,
        metadata: dict[str, Any] | None = None,
    ) -> list:
        """
        Apply a split wallet and external payment.

        Wallet and external portions must use separate idempotency keys.
        """
        applications = []

        if wallet_amount > Decimal("0.00"):
            wallet_application = cls.apply_wallet_payment(
                special_order=special_order,
                amount=wallet_amount,
                idempotency_key=wallet_idempotency_key,
                wallet_transaction_reference=wallet_transaction_reference,
                ledger_entry_reference=wallet_ledger_entry_reference,
                milestone=milestone,
                applied_by=applied_by,
                metadata={
                    "split": True,
                    "split_component": "wallet",
                    **(metadata or {}),
                },
            )
            applications.append(wallet_application)

        if external_amount > Decimal("0.00"):
            external_application = cls.apply_external_payment(
                special_order=special_order,
                amount=external_amount,
                idempotency_key=external_idempotency_key,
                payment_intent_reference=payment_intent_reference,
                payment_transaction_reference=payment_transaction_reference,
                ledger_entry_reference=external_ledger_entry_reference,
                milestone=milestone,
                applied_by=applied_by,
                metadata={
                    "split": True,
                    "split_component": "external",
                    **(metadata or {}),
                },
            )
            applications.append(external_application)

        if not applications:
            raise ValueError("Split payment must apply at least one amount.")

        return applications