from __future__ import annotations

from datetime import datetime
from typing import Optional
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from payments_processor.enums import (
    PaymentApplicationStatus,
    PaymentIntentStatus,
)
from payments_processor.models import PaymentIntent


def get_payment_intent_by_reference(
    reference: str,
) -> Optional[PaymentIntent]:
    """
    Return a payment intent by reference.
    """
    return (
        PaymentIntent.objects.select_related(
            "client",
            "website",
        )
        .filter(reference=reference)
        .first()
    )


def get_payment_intent_by_id(
    payment_intent_id: int,
) -> Optional[PaymentIntent]:
    """
    Return a payment intent by primary key.
    """
    return (
        PaymentIntent.objects.select_related(
            "website",
            "client",
        )
        .filter(pk=payment_intent_id)
        .first()
    )


def get_stale_pending_payment_intents(
    *,
    before_datetime: datetime,
) -> QuerySet[PaymentIntent]:
    """
    Return unresolved payment intents older than the given datetime.
    """
    return (
        PaymentIntent.objects.select_related(
            "client",
            "website",
        )
        .filter(
            status__in=[
                PaymentIntentStatus.PENDING,
                PaymentIntentStatus.PROCESSING,
                PaymentIntentStatus.REQUIRES_ACTION,
            ],
            created_at__lt=before_datetime,
        )
        .exclude(
            application_status=PaymentApplicationStatus.APPLIED,
        )
        .order_by("created_at")
    )


def get_active_payment_intents_for_payable(
    *,
    payable,
) -> QuerySet[PaymentIntent]:
    """
    Return active payment intents for a payable.
    """
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


def get_expired_payment_intents(
    *,
    limit: int = 100,
) -> QuerySet[PaymentIntent]:
    """
    Return payment intents that have passed their expiry time but are not
    yet in a terminal state.
    """
    now = timezone.now()

    return (
        PaymentIntent.objects.select_related(
            "website",
            "client",
        )
        .filter(expires_at__isnull=False, expires_at__lte=now)
        .exclude(
            status__in=[
                PaymentIntentStatus.SUCCEEDED,
                PaymentIntentStatus.FAILED,
                PaymentIntentStatus.CANCELED,
                PaymentIntentStatus.EXPIRED,
                PaymentIntentStatus.REFUNDED,
            ],
        )
        .order_by("expires_at")[:limit]
    )