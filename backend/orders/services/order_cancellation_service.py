from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.orders.order import Order
from orders.models.orders.order_timeline_event import (
    OrderTimelineEvent,
)
from orders.models.orders.constants import (
    ORDER_ASSIGNMENT_STATUS_RELEASED,
    ORDER_STATUS_CANCELLED,
    ORDER_TIMELINE_EVENT_CANCELLED,
)
from orders.services.policies.order_cancellation_policy import (
    OrderCancellationPolicy,
)
from orders.services.staffing.order_staffing_store import (
    OrderStaffingStore,
)
from orders.services.policies.order_status_transition_policy import (
    validate_status_transition,
)

class OrderCancellationService:
    """
    Own order cancellation workflow.

    Responsibilities:
        1. Validate cancellation eligibility.
        2. Release active assignment if present.
        3. Mark order as cancelled.
        4. Record timeline history.
        5. Provide structured metadata for downstream refund and payout
           orchestration.

    This service does not:
        1. Execute wallet refunds directly.
        2. Execute external gateway refunds directly.
        3. Reverse writer payout directly.

    Those should be delegated to payments / wallets / ledger layers.
    """

    REFUND_DESTINATION_WALLET = "wallet"
    REFUND_DESTINATION_EXTERNAL = "external_gateway"

    @classmethod
    @transaction.atomic
    def cancel_order(
        cls,
        *,
        order: Order,
        cancelled_by: Any,
        reason: str,
        refund_destination: str,
        triggered_by: Optional[Any] = None,
        notes: str = "",
        refund_amount: Optional[Decimal] = None,
    ) -> Order:
        """
        Cancel an order and perform local order domain side effects.
        """
        locked_order = cls._lock_order(order)

        OrderCancellationPolicy.validate_can_cancel(order=locked_order)
        cls._validate_actor_website(actor=cancelled_by, order=locked_order)
        cls._validate_refund_destination(
            refund_destination=refund_destination
        )

        validate_status_transition(
            from_status=locked_order.status,
            to_status=ORDER_STATUS_CANCELLED,
        )

        current_assignment = OrderStaffingStore.get_current_assignment(
            order=locked_order
        )

        released_assignment_id = None
        released_writer_id = None

        if current_assignment is not None:
            current_assignment.status = ORDER_ASSIGNMENT_STATUS_RELEASED
            current_assignment.is_current = False
            current_assignment.released_at = timezone.now()
            current_assignment.release_reason = (
                f"order_cancelled:{reason}"
            )
            current_assignment.save(
                update_fields=[
                    "status",
                    "is_current",
                    "released_at",
                    "release_reason",
                    "updated_at",
                ]
            )
            released_assignment_id = current_assignment.pk
            released_writer_id = getattr(
                current_assignment.writer,
                "pk",
                None,
            )

        locked_order.status = ORDER_STATUS_CANCELLED
        locked_order.cancelled_at = timezone.now()
        locked_order.cancelled_by = cancelled_by
        locked_order.cancellation_reason = reason

        locked_order.save(
            update_fields=[
                "status",
                "cancelled_at",
                "cancelled_by",
                "cancellation_reason",
                "updated_at",
            ]
        )

        compensation_action = cls._reverse_writer_compensation(
            order=locked_order,
            cancelled_by=cancelled_by,
        )

        cls._create_timeline_event(
            order=locked_order,
            actor=triggered_by or cancelled_by,
            metadata={
                "cancelled_by_id": getattr(cancelled_by, "pk", None),
                "reason": reason,
                "notes": notes,
                "refund_destination": refund_destination,
                "refund_amount": str(refund_amount) if refund_amount is not None else None,
                "released_assignment_id": released_assignment_id,
                "released_writer_id": released_writer_id,
                "writer_compensation_action": compensation_action,
            },
        )

        cls._trigger_refund_orchestration(
            order=locked_order,
            refund_destination=refund_destination,
            cancelled_by=cancelled_by,
            refund_amount=refund_amount,
        )

        cls._notify_cancelled(
            order=locked_order,
            actor=triggered_by or cancelled_by,
            reason=reason,
        )
        return locked_order

    @classmethod
    def _validate_refund_destination(
        cls,
        *,
        refund_destination: str,
    ) -> None:
        """
        Ensure refund destination is one of the allowed values.
        """
        allowed = {
            cls.REFUND_DESTINATION_WALLET,
            cls.REFUND_DESTINATION_EXTERNAL,
        }
        if refund_destination not in allowed:
            raise ValidationError(
                "refund_destination must be 'wallet' or "
                "'external_gateway'."
            )

    @staticmethod
    def _lock_order(order: Order) -> Order:
        """
        Lock and reload an order inside a transaction.
        """
        return Order.objects.select_for_update().get(pk=order.pk)

    @staticmethod
    def _validate_actor_website(
        *,
        actor: Any,
        order: Order,
    ) -> None:
        """
        Ensure actor belongs to the same tenant as the order.
        """
        actor_website_id = getattr(actor, "website_id", None)
        if (
            actor_website_id is not None
            and actor_website_id != order.website.pk
        ):
            raise ValidationError(
                "Actor website must match order website."
            )

    @classmethod
    def _trigger_refund_orchestration(
        cls,
        *,
        order: Order,
        refund_destination: str,
        cancelled_by,
        refund_amount: Optional[Decimal] = None,
    ) -> None:
        """
        Trigger a refund after cancellation.

        refund_amount: forfeiture-adjusted amount from OrderCancellationRequest.
        When None (direct cancellation without a request), falls back to
        order.amount_paid. Always clamped to amount_paid so we never
        refund more than was received.

        Wallet: credits immediately; updates PaymentIntent.amount_refunded.
        External gateway: creates a Refund record and queues a provider call.
        """
        import logging
        log = logging.getLogger(__name__)

        amount_paid = getattr(order, "amount_paid", None)
        if not amount_paid or amount_paid <= 0:
            return

        amount_to_refund = refund_amount if refund_amount is not None else amount_paid
        if amount_to_refund <= 0:
            return
        amount_to_refund = min(Decimal(str(amount_to_refund)), Decimal(str(amount_paid)))

        if refund_destination == cls.REFUND_DESTINATION_WALLET:
            try:
                from wallets.services.client_wallet_service import ClientWalletService
                ClientWalletService.refund_to_wallet(
                    website=order.website,
                    client=order.client,
                    amount=amount_to_refund,
                    created_by=cancelled_by,
                    description=f"Refund for cancelled order #{order.pk}",
                    reference=f"order_{order.pk}_cancellation",
                    reference_type="order_cancellation",
                    reference_id=str(order.pk),
                    metadata={
                        "order_id": order.pk,
                        "cancellation_reason": getattr(order, "cancellation_reason", ""),
                        "amount_paid": str(amount_paid),
                        "refund_amount": str(amount_to_refund),
                    },
                )
                cls._update_payment_intent_refunded(order=order, refunded=amount_to_refund)
            except Exception:
                log.exception("Wallet refund failed for order_id=%s", order.pk)

        elif refund_destination == cls.REFUND_DESTINATION_EXTERNAL:
            cls._queue_external_refund(
                order=order,
                amount=amount_to_refund,
                requested_by=cancelled_by,
            )

    @staticmethod
    def _update_payment_intent_refunded(*, order: Order, refunded: Decimal) -> None:
        import logging
        log = logging.getLogger(__name__)
        try:
            from django.contrib.contenttypes.models import ContentType
            from django.db.models import F
            from payments_processor.models.payment_intent import PaymentIntent
            from payments_processor.enums import PaymentIntentStatus

            ct = ContentType.objects.get_for_model(order.__class__)
            PaymentIntent.objects.filter(
                payable_content_type=ct,
                payable_object_id=order.pk,
                status=PaymentIntentStatus.SUCCEEDED,
            ).update(amount_refunded=F("amount_refunded") + refunded)
        except Exception:
            log.warning(
                "_update_payment_intent_refunded: failed for order %s",
                order.pk, exc_info=True,
            )

    @staticmethod
    def _queue_external_refund(*, order: Order, amount: Decimal, requested_by: Any) -> None:
        import logging
        log = logging.getLogger(__name__)
        try:
            from django.contrib.contenttypes.models import ContentType
            from django.db import transaction as db_transaction
            from payments_processor.models.payment_intent import PaymentIntent
            from payments_processor.enums import PaymentIntentStatus
            from refunds.services.refunds_processor import RefundProcessorService
            from refunds.tasks import retry_external_refund

            ct = ContentType.objects.get_for_model(order.__class__)
            pi = PaymentIntent.objects.filter(
                payable_content_type=ct,
                payable_object_id=order.pk,
                status=PaymentIntentStatus.SUCCEEDED,
            ).first()

            if pi is None:
                log.warning(
                    "_queue_external_refund: no succeeded PaymentIntent for order %s — "
                    "external refund of %s requires manual ops action.",
                    order.pk, amount,
                )
                return

            refund = RefundProcessorService.create_for_payment(
                payment_intent=pi,
                external_amount=amount,
                requested_by=requested_by,
                refund_type="automated",
                reason=f"Order #{order.pk} cancelled",
                metadata={"order_id": order.pk},
            )
            db_transaction.on_commit(lambda: retry_external_refund.delay(refund.pk))
            log.info(
                "_queue_external_refund: Refund #%s queued for order %s amount %s",
                refund.pk, order.pk, amount,
            )
        except Exception:
            log.exception(
                "_queue_external_refund: failed for order %s — manual ops required.",
                order.pk,
            )

    @classmethod
    def _reverse_writer_compensation(
        cls,
        *,
        order: Order,
        cancelled_by: Any,
    ) -> str:
        """
        Void or reverse the ORDER_EARNING CompensationEvent tied to this order.

        Window still OPEN   → void the event (excluded from the next batch close).
        Window CLOSED+      → create a REVERSAL in the next open window.

        Returns a string describing the action taken, for timeline metadata.
        """
        import logging
        log = logging.getLogger(__name__)

        try:
            from writer_compensation.models.compensation_event import CompensationEvent
            from writer_compensation.enums.compensation_enums import EventStatus, WindowStatus
            from writer_compensation.services.event_intake_service import EventIntakeService

            event = (
                CompensationEvent.objects
                .select_related("payment_window", "writer")
                .filter(source_type="order", source_id=order.pk)
                .exclude(status__in=[EventStatus.VOIDED, EventStatus.REVERSED])
                .first()
            )

            if event is None:
                log.info(
                    "_reverse_writer_compensation: no active earning event for order %s — skip.",
                    order.pk,
                )
                return "no_earning_event"

            window_status = event.payment_window.status if event.payment_window else None
            cancellation_note = f"Order #{order.pk} cancelled"

            if window_status == WindowStatus.OPEN and event.status != EventStatus.PAID:
                EventIntakeService.void_event(
                    event,
                    voided_by=cancelled_by,
                    reason=cancellation_note,
                )
                action = "voided"
            else:
                EventIntakeService.create_reversal(
                    original_event=event,
                    created_by=cancelled_by,
                    notes=cancellation_note,
                )
                action = "reversed"

            log.info(
                "_reverse_writer_compensation: %s event %s for order %s.",
                action, event.pk, order.pk,
            )

            try:
                writer = event.writer
                writer_user = getattr(writer, "user", None) or writer.account_profile.user
                from notifications_system.services.notification_service import NotificationService
                NotificationService.notify(
                    event_key="compensation.earning_reversed",
                    recipient=writer_user,
                    website=order.website,
                    context={
                        "order_id": order.pk,
                        "amount": str(abs(event.amount)),
                        "action": action,
                    },
                )
            except Exception:
                log.warning(
                    "_reverse_writer_compensation: notification failed for order %s",
                    order.pk,
                    exc_info=True,
                )

            return action

        except Exception:
            log.exception(
                "_reverse_writer_compensation: failed for order %s — compensation "
                "reversal skipped. Manual review required.",
                order.pk,
            )
            return "reversal_failed"

    @staticmethod
    def _notify_cancelled(*, order: Order, actor, reason: str) -> None:
        try:
            from orders.services.order_notification_service import (
                OrderNotificationService,
            )
            OrderNotificationService.notify_order_cancelled(
                order=order,
                cancelled_by=actor,
                reason=reason,
            )
        except Exception:
            import logging
            logging.getLogger(__name__).warning(
                "Failed to send cancellation notification for order_id=%s",
                getattr(order, "id", None),
                exc_info=True,
            )

    @staticmethod
    def _create_timeline_event(
        *,
        order: Order,
        actor: Optional[Any],
        metadata: dict[str, Any],
    ) -> OrderTimelineEvent:
        """
        Create timeline event for cancellation activity.
        """
        return OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=ORDER_TIMELINE_EVENT_CANCELLED,
            actor=actor,
            metadata=metadata,
        )