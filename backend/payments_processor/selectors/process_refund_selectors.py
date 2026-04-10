from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.db.models import Sum
from django.db.models.functions import Coalesce

from payments_processor.enums import PaymentRefundStatus
from payments_processor.models import PaymentRefund


def get_payment_refund_by_id(refund_id: int) -> Optional[PaymentRefund]:
    """
    Return a payment refund by primary key.
    """
    return (
        PaymentRefund.objects.select_related(
            "payment_intent",
            "payment_transaction",
        )
        .filter(id=refund_id)
        .first()
    )


def get_payment_refund_by_provider_refund_id(
    *,
    provider: str,
    provider_refund_id: str,
) -> Optional[PaymentRefund]:
    """
    Return a payment refund by provider refund ID.
    """
    return (
        PaymentRefund.objects.select_related(
            "payment_intent",
            "payment_transaction",
        )
        .filter(
            provider=provider,
            provider_refund_id=provider_refund_id,
        )
        .first()
    )


def get_refunds_for_payment_intent(payment_intent_id: int):
    """
    Return all refunds for a payment intent, newest first.
    """
    return (
        PaymentRefund.objects.select_related(
            "payment_transaction",
        )
        .filter(payment_intent_id=payment_intent_id)
        .order_by("-requested_at")
    )


def get_successful_refunds_for_payment_intent(payment_intent_id: int):
    """
    Return successful refunds for a payment intent.
    """
    return (
        PaymentRefund.objects.filter(
            payment_intent_id=payment_intent_id,
            status=PaymentRefundStatus.SUCCEEDED,
        )
        .order_by("-requested_at")
    )


def get_total_successful_refund_amount_for_payment_intent(
    payment_intent_id: int,
) -> Decimal:
    """
    Return the total successful refunded amount for a payment intent.
    """
    total = (
        PaymentRefund.objects.filter(
            payment_intent_id=payment_intent_id,
            status=PaymentRefundStatus.SUCCEEDED,
        )
        .aggregate(
            total=Coalesce(
                Sum("amount"),
                Decimal("0.00"),
            )
        )
        .get("total", Decimal("0.00"))
    )

    return Decimal(total)


def get_pending_refunds():
    """
    Return all refunds still pending provider completion.
    """
    return (
        PaymentRefund.objects.select_related(
            "payment_intent",
            "payment_transaction",
        )
        .filter(status=PaymentRefundStatus.PENDING)
        .order_by("requested_at")
    )