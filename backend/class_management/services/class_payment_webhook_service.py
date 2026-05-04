from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from class_management.models.class_order import ClassOrder
from class_management.models.class_payments import (
    ClassPaymentAllocation,
)
from class_management.services.class_payment_service import (
    ClassPaymentService,
)

class ClassPaymentWebhookService:
    """
    Applies successful provider payment events to class orders.
    """

    @classmethod
    @transaction.atomic
    def apply_success_event(
        cls,
        *,
        class_order: ClassOrder,
        payer,
        amount: Decimal,
        payment_intent_id: str,
        payment_transaction_id: str,
        wallet_amount: Decimal = Decimal("0.00"),
        wallet_transaction_id: str = "",
        ledger_entry_id: str = "",
        metadata: dict | None = None,
    ):
        exists = ClassPaymentAllocation.objects.filter(
            payment_intent_id=payment_intent_id,
        ).exists()

        if exists:
            return None

        return ClassPaymentService.apply_external_payment_success(
            class_order=class_order,
            payer=payer,
            amount=amount,
            payment_intent_id=payment_intent_id,
            payment_transaction_id=payment_transaction_id,
            wallet_amount=wallet_amount,
            wallet_transaction_id=wallet_transaction_id,
            ledger_entry_id=ledger_entry_id,
            metadata=metadata or {},
        )