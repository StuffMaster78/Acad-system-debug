from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from audit_logging.services.audit_service import AuditService

from payments_processor.services.payment_orchestration_service import (
    PaymentOrchestrationService,
)

from tips.enums.tip_events import TipEvents
from tips.enums.tip_status import TipStatus

from tips.models.tip import Tip

from tips.services.tip_event_service import TipEventService
from tips.services.tip_state_machine import TipStateMachine


class TipLifecycleService:
    """
    Canonical deterministic tip lifecycle manager.

    Rules:
        - ONLY this service mutates tip.status
        - ONLY PaymentOrchestrationService mutates payment state
        - ALL transitions are FSM validated
        - ALL side effects are event driven
        - ALL terminal states are idempotent
        - ALL lifecycle writes are row locked
    """

    # ------------------------------------------------------------ #
    # INTERNAL
    # ------------------------------------------------------------ #

    @staticmethod
    def _lock_tip(tip) -> Tip:
        return (
            Tip.objects.select_for_update()
            .select_related("payment_intent")
            .get(pk=tip.pk)
        )

    @staticmethod
    def _assert_not_terminal(tip) -> None:

        if tip.status in {
            TipStatus.SUCCEEDED,
            TipStatus.FAILED,
            TipStatus.CANCELLED,
        }:
            raise ValueError(
                f"Tip already in terminal state: {tip.status}"
            )

    # ------------------------------------------------------------ #
    # PAYMENT INITIATED
    # ------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def mark_payment_initiated(
        tip,
        *,
        triggered_by=None,
    ) -> Tip:

        tip = TipLifecycleService._lock_tip(tip)

        if tip.status == TipStatus.PAYMENT_INITIATED:
            return tip

        TipLifecycleService._assert_not_terminal(tip)

        payment_intent = tip.payment_intent

        # initialize provider/payment FIRST
        PaymentOrchestrationService.initialize_payment(
            payment_intent,
            triggered_by=triggered_by,
        )

        # then transition state
        TipStateMachine.transition(
            tip,
            TipStatus.PAYMENT_INITIATED,
        )

        TipEventService.emit(
            tip=tip,
            event_type=TipEvents.PAYMENT_INITIATED,
            payload={
                "tip_id": tip.pk,
                "payment_intent_id": getattr(
                    payment_intent,
                    "pk",
                    None,
                ),
            },
        )

        AuditService.record(
            action=TipEvents.PAYMENT_INITIATED,
            actor=triggered_by,
            obj=tip,
            website=getattr(tip.sender, "website", None),
            metadata={
                "tip_id": tip.pk,
                "payment_intent_id": getattr(
                    payment_intent,
                    "pk",
                    None,
                ),
            },
        )

        return tip

    # ------------------------------------------------------------ #
    # PROCESSING
    # ------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def mark_processing(
        tip,
        *,
        triggered_by=None,
    ) -> Tip:

        tip = TipLifecycleService._lock_tip(tip)

        if tip.status == TipStatus.PROCESSING:
            return tip

        TipLifecycleService._assert_not_terminal(tip)

        TipStateMachine.transition(
            tip,
            TipStatus.PROCESSING,
        )

        TipEventService.emit(
            tip=tip,
            event_type=TipEvents.PROCESSING,
            payload={
                "tip_id": tip.pk,
            },
        )

        AuditService.record(
            action=TipEvents.PROCESSING,
            actor=triggered_by,
            obj=tip,
            website=getattr(tip.sender, "website", None),
            metadata={
                "tip_id": tip.pk,
            },
        )

        return tip

    # ------------------------------------------------------------ #
    # SUCCESS
    # ------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def mark_success(
        tip,
        *,
        triggered_by=None,
        provider_transaction_id: str = "",
    ) -> Tip:

        tip = TipLifecycleService._lock_tip(tip)

        if tip.status == TipStatus.SUCCEEDED:
            return tip

        if tip.status in {
            TipStatus.FAILED,
            TipStatus.CANCELLED,
        }:
            raise ValueError(
                f"Cannot transition terminal tip state: {tip.status}"
            )

        payment_intent = tip.payment_intent

        # transition FIRST (state lock)
        TipStateMachine.transition(
            tip,
            TipStatus.SUCCEEDED,
        )

        tip.paid_at = timezone.now()

        tip.save(
            update_fields=[
                "paid_at",
            ]
        )

        # finalize payment/wallet lifecycle
        PaymentOrchestrationService.mark_payment_success(
            payment_intent,
            provider_transaction_id=provider_transaction_id,
            triggered_by=triggered_by,
        )

        TipEventService.emit(
            tip=tip,
            event_type=TipEvents.SUCCEEDED,
            payload={
                "tip_id": tip.pk,
                "payment_intent_id": getattr(
                    payment_intent,
                    "pk",
                    None,
                ),
                "provider_transaction_id": provider_transaction_id,
            },
        )

        AuditService.record(
            action=TipEvents.SUCCEEDED,
            actor=triggered_by,
            obj=tip,
            website=getattr(tip.sender, "website", None),
            metadata={
                "tip_id": tip.pk,
                "payment_intent_id": getattr(
                    payment_intent,
                    "pk",
                    None,
                ),
                "provider_transaction_id": provider_transaction_id,
            },
        )

        return tip

    # ------------------------------------------------------------ #
    # FAILURE
    # ------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def mark_failed(
        tip,
        *,
        reason: str = "",
        triggered_by=None,
    ) -> Tip:

        tip = TipLifecycleService._lock_tip(tip)

        if tip.status == TipStatus.FAILED:
            return tip

        if tip.status in {
            TipStatus.SUCCEEDED,
            TipStatus.CANCELLED,
        }:
            raise ValueError(
                f"Cannot transition terminal tip state: {tip.status}"
            )

        payment_intent = tip.payment_intent

        # transition FIRST
        TipStateMachine.transition(
            tip,
            TipStatus.FAILED,
        )

        tip.failed_at = timezone.now()
        tip.failure_reason = reason

        tip.save(
            update_fields=[
                "failed_at",
                "failure_reason",
            ]
        )

        # finalize rollback/payment failure
        PaymentOrchestrationService.mark_payment_failed(
            payment_intent,
            failure_reason=reason,
            triggered_by=triggered_by,
        )

        TipEventService.emit(
            tip=tip,
            event_type=TipEvents.FAILED,
            payload={
                "tip_id": tip.pk,
                "reason": reason,
                "payment_intent_id": getattr(
                    payment_intent,
                    "pk",
                    None,
                ),
            },
        )

        AuditService.record(
            action=TipEvents.FAILED,
            actor=triggered_by,
            obj=tip,
            website=getattr(tip.sender, "website", None),
            metadata={
                "tip_id": tip.pk,
                "reason": reason,
                "payment_intent_id": getattr(
                    payment_intent,
                    "pk",
                    None,
                ),
            },
        )

        return tip

    # ------------------------------------------------------------ #
    # CANCELLED
    # ------------------------------------------------------------ #

    @staticmethod
    @transaction.atomic
    def mark_cancelled(
        tip,
        *,
        reason: str = "",
        triggered_by=None,
    ) -> Tip:

        tip = TipLifecycleService._lock_tip(tip)

        if tip.status == TipStatus.CANCELLED:
            return tip

        if tip.status in {
            TipStatus.SUCCEEDED,
            TipStatus.FAILED,
        }:
            raise ValueError(
                f"Cannot transition terminal tip state: {tip.status}"
            )

        payment_intent = tip.payment_intent

        TipStateMachine.transition(
            tip,
            TipStatus.CANCELLED,
        )

        PaymentOrchestrationService.mark_payment_failed(
            payment_intent,
            failure_reason=reason or "cancelled",
            triggered_by=triggered_by,
        )

        TipEventService.emit(
            tip=tip,
            event_type=TipEvents.CANCELLED,
            payload={
                "tip_id": tip.pk,
                "reason": reason,
                "payment_intent_id": getattr(
                    payment_intent,
                    "pk",
                    None,
                ),
            },
        )

        AuditService.record(
            action=TipEvents.CANCELLED,
            actor=triggered_by,
            obj=tip,
            website=getattr(tip.sender, "website", None),
            metadata={
                "tip_id": tip.pk,
                "reason": reason,
                "payment_intent_id": getattr(
                    payment_intent,
                    "pk",
                    None,
                ),
            },
        )

        return tip