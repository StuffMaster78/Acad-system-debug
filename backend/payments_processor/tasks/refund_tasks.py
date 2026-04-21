from __future__ import annotations

import logging
from typing import Any

from celery import shared_task

from payments_processor.exceptions import PaymentError
from payments_processor.selectors.process_refund_selectors import (
    get_payment_refund_by_id,
)
from payments_processor.services.refund_application_service import (
    RefundApplicationService,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def apply_refund_task(
    self,
    refund_id: int,
    triggered_by_id: int | None = None,
) -> dict[str, Any]:
    """
    Apply a successful refund internally.

    This task is intentionally separate from provider-side refund
    execution so that:
    1. provider execution can succeed independently
    2. internal reversal can be retried safely
    3. wallet and ledger operations stay idempotent
    """
    refund = get_payment_refund_by_id(refund_id)
    if refund is None:
        raise PaymentError(f"Refund '{refund_id}' was not found.")

    # NOTE:
    # You can later resolve triggered_by from the user model if needed.
    triggered_by = None
    _ = triggered_by_id

    result = RefundApplicationService.apply_refund(
        refund=refund,
        triggered_by=triggered_by,
    )

    logger.info(
        "Refund application completed for refund_id=%s, "
        "payment_intent_id=%s, already_applied=%s",
        refund_id,
        refund.payment_intent.pk,
        result.get("already_applied"),
    )

    return result