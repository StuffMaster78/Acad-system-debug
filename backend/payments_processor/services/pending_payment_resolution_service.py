from __future__ import annotations

from typing import Any, cast
from datetime import timedelta
from django.utils import timezone

from django.db import transaction as db_transaction

from payments_processor.enums import PaymentIntentStatus
from payments_processor.exceptions import PaymentError
from payments_processor.selectors.payment_allocation_selectors import (
    get_wallet_allocation_for_payable,
)
from payments_processor.selectors.payment_intent_selectors import (
    get_expired_payment_intents,
    get_stale_pending_payment_intents,
)
from payments_processor.services.payment_allocation_application_service import (
    PaymentAllocationApplicationService,
)
from payments_processor.services.payment_verification_service import (
    PaymentVerificationService,
)
from payments_processor.tasks.payment_application_tasks import (
    apply_payment_intent_task,
)


class PendingPaymentResolutionService:
    """
    Resolve stale and expired payment intents.

    Responsibilities:
    1. re-check stale pending intents against provider
    2. enqueue internal application for successful intents
    3. release wallet allocations for failed or expired intents
    4. mark expired intents cleanly
    """

    @classmethod
    def resolve_stale_pending_payments(
        cls,
        *,
        older_than_minutes: int = 15,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Re-verify stale pending payment intents and resolve them.
        """
        cutoff = timezone.now() - timedelta(
            minutes=older_than_minutes
        )

        intents = get_stale_pending_payment_intents(
            before_datetime=cutoff,
        )[:limit]

        summary = {
            "checked": 0,
            "succeeded": 0,
            "failed": 0,
            "expired": 0,
            "still_pending": 0,
            "errors": 0,
        }

        for payment_intent in intents:
            summary["checked"] += 1

            try:
                result = cls.resolve_payment_intent(
                    payment_intent=payment_intent,
                )
            except Exception:
                summary["errors"] += 1
                continue

            final_status = str(result.get("final_status") or "")

            if final_status == PaymentIntentStatus.SUCCEEDED:
                summary["succeeded"] += 1
            elif final_status == PaymentIntentStatus.FAILED:
                summary["failed"] += 1
            elif final_status == PaymentIntentStatus.EXPIRED:
                summary["expired"] += 1
            else:
                summary["still_pending"] += 1

        return summary

    @classmethod
    def expire_elapsed_payment_intents(
        cls,
        *,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Mark elapsed intents as expired and release wallet allocations.
        """
        intents = get_expired_payment_intents(limit=limit)

        summary = {
            "checked": 0,
            "expired": 0,
            "released_wallet_allocations": 0,
            "errors": 0,
        }

        for payment_intent in intents:
            summary["checked"] += 1

            try:
                released = cls._expire_payment_intent(
                    payment_intent=payment_intent,
                )
            except Exception:
                summary["errors"] += 1
                continue

            summary["expired"] += 1
            if released:
                summary["released_wallet_allocations"] += 1

        return summary

    @classmethod
    @db_transaction.atomic
    def resolve_payment_intent(
        cls,
        *,
        payment_intent,
    ) -> dict[str, Any]:
        """
        Resolve one payment intent by verifying it against the provider.

        Behavior:
        1. verify current provider state
        2. enqueue application if succeeded
        3. release wallet allocation if failed
        4. leave pending if still unresolved
        """
        verification_result = (
            PaymentVerificationService.verify_payment_intent(
                payment_intent=payment_intent,
                create_transaction=True,
            )
        )

        final_status = payment_intent.status

        if final_status == PaymentIntentStatus.SUCCEEDED:
            payment_task = cast(Any, apply_payment_intent_task)

            def enqueue_payment_application() -> None:
                payment_task.delay(payment_intent.pk)

            db_transaction.on_commit(enqueue_payment_application)

        elif final_status in {
            PaymentIntentStatus.FAILED,
            PaymentIntentStatus.CANCELED,
            PaymentIntentStatus.EXPIRED,
        }:
            cls._release_wallet_allocation_if_present(
                payment_intent=payment_intent,
                reason=f"payment_intent_{final_status}",
            )

        return {
            "payment_intent_id": payment_intent.pk,
            "reference": payment_intent.reference,
            "final_status": final_status,
            "verification_result": verification_result,
        }

    @classmethod
    @db_transaction.atomic
    def _expire_payment_intent(
        cls,
        *,
        payment_intent,
    ) -> bool:
        """
        Expire one payment intent and release wallet allocation if present.
        """
        if payment_intent.status == PaymentIntentStatus.EXPIRED:
            return False

        payment_intent.status = PaymentIntentStatus.EXPIRED
        payment_intent.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return cls._release_wallet_allocation_if_present(
            payment_intent=payment_intent,
            reason="payment_intent_expired",
        )

    @classmethod
    def _release_wallet_allocation_if_present(
        cls,
        *,
        payment_intent,
        reason: str,
    ) -> bool:
        """
        Release wallet allocation for the payable if one exists and is
        releasable.
        """
        payable = payment_intent.payable
        if payable is None:
            return False

        wallet_allocation = get_wallet_allocation_for_payable(
            payable=payable,
        )
        if wallet_allocation is None:
            return False

        try:
            PaymentAllocationApplicationService.release_wallet_allocation(
                wallet_allocation=wallet_allocation,
                reason=reason,
            )
        except PaymentError:
            return False

        return True