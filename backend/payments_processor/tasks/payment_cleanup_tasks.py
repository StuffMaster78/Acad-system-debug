from __future__ import annotations

import logging
from typing import Any

from celery import shared_task

from payments_processor.services.pending_payment_resolution_service import (
    PendingPaymentResolutionService,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def resolve_stale_pending_payments_task(
    self,
    older_than_minutes: int = 15,
    limit: int = 100,
) -> dict[str, Any]:
    """
    Re-check stale pending payment intents and resolve them.

    This will:
    1. verify with provider
    2. apply successful payments
    3. release wallet allocations for failed ones
    """
    result = PendingPaymentResolutionService.resolve_stale_pending_payments(
        older_than_minutes=older_than_minutes,
        limit=limit,
    )

    logger.info(
        (
            "Stale payment resolution: checked=%s succeeded=%s "
            "failed=%s expired=%s still_pending=%s errors=%s"
        ),
        result.get("checked"),
        result.get("succeeded"),
        result.get("failed"),
        result.get("expired"),
        result.get("still_pending"),
        result.get("errors"),
    )

    return result


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def expire_elapsed_payment_intents_task(
    self,
    limit: int = 100,
) -> dict[str, Any]:
    """
    Expire payment intents that have passed their expiry time.

    This will:
    1. mark intent as EXPIRED
    2. release wallet allocations if present
    """
    result = PendingPaymentResolutionService.expire_elapsed_payment_intents(
        limit=limit,
    )

    logger.info(
        (
            "Expired intents: checked=%s expired=%s "
            "released_wallet_allocations=%s errors=%s"
        ),
        result.get("checked"),
        result.get("expired"),
        result.get("released_wallet_allocations"),
        result.get("errors"),
    )

    return result

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def cancel_orphaned_prewarm_sessions_task(
    self,
    older_than_hours: int = 2,
    limit: int = 200,
) -> dict:
    """
    Cancel PENDING PaymentIntents that were pre-warmed (no payable linked)
    but never converted into an order. Runs hourly via Celery beat.
    """
    from django.utils import timezone
    from datetime import timedelta
    from payments_processor.models import PaymentIntent
    from payments_processor.enums import PaymentIntentStatus
    from payments_processor.services.payment_intent_service import PaymentIntentService

    cutoff = timezone.now() - timedelta(hours=older_than_hours)
    orphans = list(
        PaymentIntent.objects
        .filter(
            status=PaymentIntentStatus.PENDING,
            payable_object_id__isnull=True,
            created_at__lt=cutoff,
        )
        .order_by("created_at")[:limit]
    )

    cancelled = errors = 0
    for intent in orphans:
        try:
            PaymentIntentService.cancel_intent(payment_intent=intent)
            cancelled += 1
        except Exception as exc:
            logger.warning("Could not cancel orphaned prewarm %s: %s", intent.reference, exc)
            errors += 1

    logger.info("Orphaned prewarm cleanup: cancelled=%s errors=%s", cancelled, errors)
    return {"cancelled": cancelled, "errors": errors}
