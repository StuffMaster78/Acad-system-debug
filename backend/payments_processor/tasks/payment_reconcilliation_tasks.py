from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from celery import shared_task
from django.utils import timezone

from payments_processor.services.payment_reconciliation_service import (
    PaymentReconciliationService,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def reconcile_stale_payment_intents_task(
    self,
    older_than_minutes: int = 15,
    limit: int = 100,
) -> dict[str, Any]:
    """
    Reconcile stale unresolved payment intents against provider state.
    """
    cutoff = timezone.now() - timedelta(
        minutes=older_than_minutes,
    )

    result = PaymentReconciliationService.reconcile_stale_payment_intents(
        before_datetime=cutoff,
        limit=limit,
    )

    logger.info(
        (
            "Payment reconciliation: checked=%s changed=%s "
            "unchanged=%s errors=%s"
        ),
        result.get("checked"),
        result.get("changed"),
        result.get("unchanged"),
        result.get("errors"),
    )

    return result


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def reconcile_pending_refunds_task(
    self,
    limit: int = 100,
) -> dict[str, Any]:
    """
    Reconcile pending refunds.
    """
    result = PaymentReconciliationService.reconcile_pending_refunds(
        limit=limit,
    )

    logger.info(
        (
            "Refund reconciliation: checked=%s changed=%s "
            "unchanged=%s errors=%s"
        ),
        result.get("checked"),
        result.get("changed"),
        result.get("unchanged"),
        result.get("errors"),
    )

    return result


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def reconcile_payment_intent_by_id_task(
    self,
    payment_intent_id: int,
) -> dict[str, Any]:
    """
    Reconcile one payment intent on demand.
    """
    result = PaymentReconciliationService.reconcile_payment_intent_by_id(
        payment_intent_id=payment_intent_id,
    )

    logger.info(
        "On-demand payment reconciliation completed for intent=%s "
        "changed=%s",
        payment_intent_id,
        result.get("changed"),
    )

    return result