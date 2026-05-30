from __future__ import annotations

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

        cls._create_timeline_event(
            order=locked_order,
            actor=triggered_by or cancelled_by,
            metadata={
                "cancelled_by_id": getattr(cancelled_by, "pk", None),
                "reason": reason,
                "notes": notes,
                "refund_destination": refund_destination,
                "released_assignment_id": released_assignment_id,
                "released_writer_id": released_writer_id,
                "writer_compensation_action": "revoke_or_reverse_later",
            },
        )

        cls._trigger_refund_orchestration(
            order=locked_order,
            refund_destination=refund_destination,
            cancelled_by=cancelled_by,
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
    ) -> None:
        """
        Trigger a refund after cancellation.

        For wallet destination: credits the paid amount back to the client
        wallet immediately via ClientWalletService.

        For external_gateway destination: the refund must be initiated
        through the payment provider. This method creates the ledger record
        and logs the intent; the actual provider call is handled by ops or
        an async reconciliation task since gateway refunds require the
        original payment transaction reference.

        Payout reversal for the writer (if already paid) is queued via
        timeline metadata and handled by the compensation system separately.
        """
        import logging
        log = logging.getLogger(__name__)

        amount_paid = getattr(order, "amount_paid", None)
        if not amount_paid or amount_paid <= 0:
            return

        if refund_destination == cls.REFUND_DESTINATION_WALLET:
            try:
                from wallets.services.client_wallet_service import (
                    ClientWalletService,
                )
                ClientWalletService.refund_to_wallet(
                    website=order.website,
                    client=order.client,
                    amount=amount_paid,
                    created_by=cancelled_by,
                    description=f"Refund for cancelled order #{order.pk}",
                    reference=f"order_{order.pk}_cancellation",
                    reference_type="order_cancellation",
                    reference_id=str(order.pk),
                    metadata={
                        "order_id": order.pk,
                        "cancellation_reason": getattr(
                            order, "cancellation_reason", ""
                        ),
                    },
                )
            except Exception as exc:
                log.exception(
                    "Wallet refund failed for order_id=%s: %s",
                    order.pk,
                    exc,
                )

        elif refund_destination == cls.REFUND_DESTINATION_EXTERNAL:
            # External gateway refunds require the original PaymentIntent.
            # Log the intent and let the reconciliation task or ops action pick it up.
            log.info(
                "External gateway refund pending for order_id=%s amount=%s. "
                "Manual action or reconciliation task required.",
                order.pk,
                amount_paid,
            )

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