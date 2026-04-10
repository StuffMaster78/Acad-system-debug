from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from celery import shared_task

from payments_processor.enums import (
    PaymentApplicationStatus,
    PaymentIntentStatus,
)
from payments_processor.exceptions import PaymentError
from payments_processor.selectors.payment_intent_selectors import (
    get_payment_intent_by_id,
)
from payments_processor.services.payment_application_service import (
    PaymentApplicationService,
)

logger = logging.getLogger(__name__)


def _resolve_payable_total_amount(payment_intent) -> Decimal:
    """
    Resolve the total amount required to settle the payable.

    For now:
    1. prefer explicit metadata override
    2. otherwise use payable.total_amount / payable.amount / payment_intent.amount
    """
    metadata = payment_intent.metadata or {}

    if "payable_total_amount" in metadata:
        return Decimal(str(metadata["payable_total_amount"]))

    payable = payment_intent.payable
    if payable is not None:
        if hasattr(payable, "total_amount"):
            return Decimal(str(payable.total_amount))
        if hasattr(payable, "amount"):
            return Decimal(str(payable.amount))
        if hasattr(payable, "price"):
            return Decimal(str(payable.price))

    return Decimal(str(payment_intent.amount))


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def apply_payment_intent_task(self, payment_intent_id: int) -> dict[str, Any]:
    """
    Apply a successful payment intent internally.

    Safe to retry because:
    1. PaymentApplicationGuardService prevents double application
    2. Allocation application is idempotent
    """
    payment_intent = get_payment_intent_by_id(payment_intent_id)
    if payment_intent is None:
        raise PaymentError(
            f"Payment intent '{payment_intent_id}' not found."
        )

    if payment_intent.status != PaymentIntentStatus.SUCCEEDED:
        logger.info(
            "Skipping application for payment intent '%s' because status is '%s'.",
            payment_intent.reference,
            payment_intent.status,
        )
        return {
            "payment_intent_id": payment_intent_id,
            "skipped": True,
            "reason": f"status={payment_intent.status}",
        }

    if payment_intent.application_status == PaymentApplicationStatus.APPLIED:
        return {
            "payment_intent_id": payment_intent_id,
            "skipped": True,
            "reason": "already_applied",
        }

    total_amount = _resolve_payable_total_amount(payment_intent)

    payment_intent.application_status = PaymentApplicationStatus.APPLYING
    payment_intent.application_attempts += 1
    payment_intent.application_error = ""
    payment_intent.save(
        update_fields=[
            "application_status",
            "application_attempts",
            "application_error",
            "updated_at",
        ]
    )

    try:
        result = PaymentApplicationService.apply_payment(
            payment_intent=payment_intent,
            total_amount=total_amount,
        )
    except Exception as exc:
        payment_intent.application_status = (
            PaymentApplicationStatus.APPLICATION_FAILED
        )
        payment_intent.application_error = str(exc)
        payment_intent.save(
            update_fields=[
                "application_status",
                "application_error",
                "updated_at",
            ]
        )

        logger.exception(
            "Payment application failed for '%s': %s",
            payment_intent.reference,
            exc,
        )
        raise

    return {
        "payment_intent_id": payment_intent.pk,
        "reference": payment_intent.reference,
        "application_status": payment_intent.application_status,
        "result": result,
    }