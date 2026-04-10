from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from celery import shared_task
from django.utils import timezone

from payments_processor.constants import (
    PENDING_PAYMENT_RESOLUTION_BATCH_SIZE,
    PENDING_PAYMENT_TIMEOUT_MINUTES,
)
from payments_processor.enums import PaymentIntentStatus
from payments_processor.selectors.payment_intent_selectors import (
    get_stale_pending_payment_intents,
)
from payments_processor.services.payment_intent_service import PaymentIntentService
from payments_processor.services.payment_verification_service import (
    PaymentVerificationService,
)

logger = logging.getLogger(__name__)


def _resolve_stale_pending_payment_intents() -> dict[str, Any]:
    cutoff = timezone.now() - timedelta(
        minutes=PENDING_PAYMENT_TIMEOUT_MINUTES
    )

    payment_intents = get_stale_pending_payment_intents(
        before_datetime=cutoff
    )[:PENDING_PAYMENT_RESOLUTION_BATCH_SIZE]

    results = {
        "checked": 0,
        "verified_succeeded": 0,
        "verified_failed": 0,
        "expired": 0,
        "still_pending": 0,
        "errors": 0,
        "references": [],
    }

    for payment_intent in payment_intents:
        results["checked"] += 1

        try:
            verification_result = (
                PaymentVerificationService.verify_payment_intent(
                    payment_intent=payment_intent,
                    create_transaction=True,
                )
            )

            verified_status = verification_result["verified_status"]
            results["references"].append(payment_intent.reference)

            if verified_status == PaymentIntentStatus.SUCCEEDED:
                results["verified_succeeded"] += 1
                continue

            if verified_status == PaymentIntentStatus.FAILED:
                results["verified_failed"] += 1
                continue

            if verified_status == PaymentIntentStatus.PENDING:
                if (
                    payment_intent.expires_at is not None
                    and payment_intent.expires_at <= timezone.now()
                ):
                    PaymentIntentService.expire_intent(
                        payment_intent=payment_intent
                    )
                    results["expired"] += 1
                else:
                    results["still_pending"] += 1
                continue

            results["still_pending"] += 1

        except Exception as exc:
            results["errors"] += 1
            logger.exception(
                "Failed resolving pending payment intent '%s': %s",
                payment_intent.reference,
                exc,
            )

    return results


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def resolve_stale_pending_payment_intents_task(self) -> dict[str, Any]:
    """
    Celery task wrapper for stale pending payment resolution.
    """
    return _resolve_stale_pending_payment_intents()