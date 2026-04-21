from __future__ import annotations

from typing import Any

from payments_processor.enums import (
    PaymentIntentStatus,
    PaymentRefundStatus,
)
from payments_processor.selectors.payment_intent_selectors import (
    get_payment_intent_by_id,
    get_stale_pending_payment_intents,
)
from payments_processor.selectors.process_refund_selectors import (
    get_pending_refunds,
)
from payments_processor.services.payment_verification_service import (
    PaymentVerificationService,
)
from payments_processor.services.refund_execution_service import (
    RefundExecutionService,
)


class PaymentReconciliationService:
    """
    Reconcile provider truth against internal payment and refund state.

    Responsibilities:
    1. re-check stale pending payment intents
    2. re-check stale pending refunds
    3. surface mismatches between provider and internal status
    """

    @classmethod
    def reconcile_payment_intent(
        cls,
        *,
        payment_intent,
    ) -> dict[str, Any]:
        """
        Reconcile one payment intent against provider state.
        """
        previous_status = payment_intent.status

        verification_result = PaymentVerificationService.verify_payment_intent(
            payment_intent=payment_intent,
            create_transaction=True,
        )

        return {
            "payment_intent_id": payment_intent.pk,
            "reference": payment_intent.reference,
            "previous_status": previous_status,
            "current_status": payment_intent.status,
            "changed": previous_status != payment_intent.status,
            "verification_result": verification_result,
        }

    @classmethod
    def reconcile_pending_refund(
        cls,
        *,
        refund,
    ) -> dict[str, Any]:
        """
        Reconcile one pending refund.

        Current strategy:
        1. re-run provider refund execution only if your provider supports
           idempotent refund lookup via refund execution path
        2. otherwise leave as pending and rely on webhook/provider updates

        This method is conservative by default.
        """
        return {
            "refund_id": refund.pk,
            "payment_intent_id": refund.payment_intent.pk,
            "status": refund.status,
            "changed": False,
            "message": (
                "Pending refund reconciliation not yet provider-specific. "
                "Keep webhook path and provider polling aligned."
            ),
        }

    @classmethod
    def reconcile_stale_payment_intents(
        cls,
        *,
        before_datetime,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Reconcile stale unresolved payment intents.
        """
        intents = get_stale_pending_payment_intents(
            before_datetime=before_datetime,
        )[:limit]

        summary = {
            "checked": 0,
            "changed": 0,
            "unchanged": 0,
            "errors": 0,
            "results": [],
        }

        for payment_intent in intents:
            summary["checked"] += 1

            try:
                result = cls.reconcile_payment_intent(
                    payment_intent=payment_intent,
                )
            except Exception as exc:
                summary["errors"] += 1
                summary["results"].append(
                    {
                        "payment_intent_id": payment_intent.pk,
                        "reference": payment_intent.reference,
                        "error": str(exc),
                    }
                )
                continue

            if result["changed"]:
                summary["changed"] += 1
            else:
                summary["unchanged"] += 1

            summary["results"].append(result)

        return summary

    @classmethod
    def reconcile_pending_refunds(
        cls,
        *,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Reconcile pending refunds.
        """
        refunds = get_pending_refunds()[:limit]

        summary = {
            "checked": 0,
            "changed": 0,
            "unchanged": 0,
            "errors": 0,
            "results": [],
        }

        for refund in refunds:
            summary["checked"] += 1

            try:
                result = cls.reconcile_pending_refund(refund=refund)
            except Exception as exc:
                summary["errors"] += 1
                summary["results"].append(
                    {
                        "refund_id": refund.pk,
                        "payment_intent_id": refund.payment_intent.pk,
                        "error": str(exc),
                    }
                )
                continue

            if result["changed"]:
                summary["changed"] += 1
            else:
                summary["unchanged"] += 1

            summary["results"].append(result)

        return summary

    @classmethod
    def reconcile_payment_intent_by_id(
        cls,
        *,
        payment_intent_id: int,
    ) -> dict[str, Any]:
        """
        Reconcile one payment intent by ID.
        """
        payment_intent = get_payment_intent_by_id(payment_intent_id)
        if payment_intent is None:
            raise ValueError(
                f"Payment intent '{payment_intent_id}' was not found."
            )

        return cls.reconcile_payment_intent(
            payment_intent=payment_intent,
        )