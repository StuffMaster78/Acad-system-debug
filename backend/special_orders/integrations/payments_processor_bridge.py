from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from payments_processor.models import PaymentIntent, PaymentTransaction
from special_orders.models import SpecialOrder
from special_orders.services.new_services.special_order_payment_orchestration_service import (
    SpecialOrderPaymentOrchestrationService,
)


class SpecialOrderPaymentsProcessorBridge:
    """
    Bridge successful payments_processor transactions into special_orders.

    payments_processor owns provider verification and transaction records.
    special_orders owns funding application.
    Apply successful payments_processor transactions to special orders.

    payments_processor owns:
        provider verification
        transaction records
        ledger posting

    special_orders owns:
        funding application
        milestone updates
        delivery readiness
    """

    @classmethod
    @transaction.atomic
    def apply_successful_transaction(
        cls,
        *,
        payment_intent: PaymentIntent,
        payment_transaction: PaymentTransaction,
        ledger_entry_reference: str,
        triggered_by=None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Apply a successful external payment to a special order.
        """
        special_order = cls._get_special_order(
            payment_intent=payment_intent,
        )

        idempotency_key = cls._build_idempotency_key(
            payment_transaction=payment_transaction,
        )

        return SpecialOrderPaymentOrchestrationService.apply_external_payment(
            special_order=special_order,
            amount=Decimal(str(payment_transaction.amount)),
            idempotency_key=idempotency_key,
            payment_intent_reference=str(payment_intent.pk),
            payment_transaction_reference=str(payment_transaction.pk),
            ledger_entry_reference=ledger_entry_reference,
            applied_by=triggered_by,
            metadata={
                "source": "payments_processor_webhook",
                "payment_intent_id": payment_intent.pk,
                "payment_transaction_id": payment_transaction.pk,
                **(metadata or {}),
            },
        )

    @staticmethod
    def _get_special_order(
        *,
        payment_intent: PaymentIntent,
    ) -> SpecialOrder:
        """
        Resolve the special order from PaymentIntent metadata.
        """
        payable = getattr(payment_intent, "payable", None)

        if isinstance(payable, SpecialOrder):
            return SpecialOrder.objects.select_for_update().get(
                id=payable.id,
                website=payable.website,
            )
        
        metadata = payment_intent.metadata or {}

        payable_type = metadata.get("payable_type")
        payable_id = metadata.get("payable_id")

        if payable_type != "special_order":
            raise ValueError(
                "PaymentIntent is not for a special order."
            )

        if payable_id is None:
            raise ValueError(
                "PaymentIntent missing payable_id."
            )

        return SpecialOrder.objects.select_for_update().get(
            id=payable_id,
            website=payment_intent.website,
        )

    @staticmethod
    def _build_idempotency_key(
        *,
        payment_transaction: PaymentTransaction,
    ) -> str:
        """
        Build stable idempotency key for special order payment application.
        """
        return f"payments_processor:transaction:{payment_transaction.pk}"