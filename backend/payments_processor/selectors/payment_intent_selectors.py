from __future__ import annotations

from typing import Optional

from django.contrib.contenttypes.models import ContentType

from payments_processor.enums import PaymentIntentStatus
from payments_processor.models import PaymentIntent


def get_payment_intent_by_reference(reference: str) -> Optional[PaymentIntent]:
    return (
        PaymentIntent.objects.select_related("customer")
        .filter(reference=reference)
        .first()
    )


def get_payment_intent_by_id(payment_intent_id: int) -> Optional[PaymentIntent]:
    return (
        PaymentIntent.objects.select_related("customer")
        .filter(id=payment_intent_id)
        .first()
    )


def get_stale_pending_payment_intents(*, before_datetime):
    return (
        PaymentIntent.objects.select_related("customer")
        .filter(
            status=PaymentIntentStatus.PENDING,
            created_at__lt=before_datetime,
        )
        .order_by("created_at")
    )


def get_active_payment_intents_for_payable(*, payable):
    content_type = ContentType.objects.get_for_model(payable)

    return (
        PaymentIntent.objects.filter(
            payable_content_type=content_type,
            payable_object_id=payable.pk,
            status__in=[
                PaymentIntentStatus.CREATED,
                PaymentIntentStatus.PENDING,
                PaymentIntentStatus.PROCESSING,
                PaymentIntentStatus.REQUIRES_ACTION,
            ],
        )
        .order_by("-created_at")
    )