from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from class_management.models import (
    ClassInstallment,
    ClassOrder,
    ClassPaymentAllocation,
)
from class_management.services.class_payment_service import ClassPaymentService


class ClassPaymentWebhookIntegrationService:
    """
    Idempotent bridge from payments_processor webhooks to class payments.
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
        installment: ClassInstallment | None = None,
        wallet_amount: Decimal = Decimal("0.00"),
        wallet_transaction_id: str = "",
        ledger_entry_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ClassPaymentAllocation | None:
        """
        Apply a successful provider event once.

        The amount argument represents the external provider amount. If this
        was a split payment, wallet_amount is added by ClassPaymentService.
        """
        if cls._already_applied(
            payment_intent_id=payment_intent_id,
            payment_transaction_id=payment_transaction_id,
        ):
            return None

        return ClassPaymentService.apply_external_payment_success(
            class_order=class_order,
            payer=payer,
            amount=amount,
            payment_intent_id=payment_intent_id,
            payment_transaction_id=payment_transaction_id,
            installment=installment,
            wallet_amount=wallet_amount,
            wallet_transaction_id=wallet_transaction_id,
            ledger_entry_id=ledger_entry_id,
            metadata=metadata or {},
        )

    @staticmethod
    def _already_applied(
        *,
        payment_intent_id: str,
        payment_transaction_id: str,
    ) -> bool:
        """
        Return whether this provider event has already been applied.
        """
        query = ClassPaymentAllocation.objects.all()

        if payment_intent_id:
            if query.filter(payment_intent_id=payment_intent_id).exists():
                return True

        if payment_transaction_id:
            if query.filter(
                payment_transaction_id=payment_transaction_id,
            ).exists():
                return True

        return False