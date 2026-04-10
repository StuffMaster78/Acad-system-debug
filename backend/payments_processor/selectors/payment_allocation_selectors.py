from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.db.models.functions import Coalesce

from payments_processor.enums import PaymentAllocationStatus, PaymentAllocationType
from payments_processor.models import PaymentAllocation


def get_payment_allocation_by_reference(
    reference: str,
) -> Optional[PaymentAllocation]:
    """
    Return a payment allocation by reference.
    """
    return (
        PaymentAllocation.objects.select_related(
            "customer",
            "wallet",
            "payment_intent",
        )
        .filter(reference=reference)
        .first()
    )


def get_payment_allocation_by_payment_intent_id(
    payment_intent_id: int,
) -> Optional[PaymentAllocation]:
    """
    Return the external payment allocation linked to a payment intent.
    """
    return (
        PaymentAllocation.objects.select_related(
            "customer",
            "wallet",
            "payment_intent",
        )
        .filter(payment_intent_id=payment_intent_id)
        .first()
    )


def get_allocations_for_payable(*, payable):
    """
    Return all allocations for a payable, oldest first.
    """
    content_type = ContentType.objects.get_for_model(payable)

    return (
        PaymentAllocation.objects.select_related(
            "customer",
            "wallet",
            "payment_intent",
        )
        .filter(
            payable_content_type=content_type,
            payable_object_id=payable.pk,
        )
        .order_by("created_at")
    )


def get_wallet_allocation_for_payable(*, payable) -> Optional[PaymentAllocation]:
    """
    Return the wallet allocation for a payable if it exists.
    """
    content_type = ContentType.objects.get_for_model(payable)

    return (
        PaymentAllocation.objects.select_related(
            "customer",
            "wallet",
            "payment_intent",
        )
        .filter(
            payable_content_type=content_type,
            payable_object_id=payable.pk,
            allocation_type=PaymentAllocationType.WALLET,
        )
        .first()
    )


def get_external_allocation_for_payable(*, payable) -> Optional[PaymentAllocation]:
    """
    Return the external payment allocation for a payable if it exists.
    """
    content_type = ContentType.objects.get_for_model(payable)

    return (
        PaymentAllocation.objects.select_related(
            "customer",
            "wallet",
            "payment_intent",
        )
        .filter(
            payable_content_type=content_type,
            payable_object_id=payable.pk,
            allocation_type=PaymentAllocationType.EXTERNAL_PAYMENT,
        )
        .first()
    )


def get_applied_total_for_payable(*, payable) -> Decimal:
    """
    Return total applied allocation amount for a payable.
    """
    content_type = ContentType.objects.get_for_model(payable)

    total = (
        PaymentAllocation.objects.filter(
            payable_content_type=content_type,
            payable_object_id=payable.pk,
            status=PaymentAllocationStatus.APPLIED,
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


def payable_is_fully_allocated(
    *,
    payable,
    total_amount: Decimal,
) -> bool:
    """
    Return True if applied allocations cover the payable amount.
    """
    applied_total = get_applied_total_for_payable(payable=payable)
    return applied_total >= total_amount