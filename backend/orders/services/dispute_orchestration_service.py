from __future__ import annotations

from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.disputes.order_dispute import OrderDispute
from orders.models.disputes.order_dispute_event import OrderDisputeEvent
from orders.models.disputes.order_dispute_resolution import (
    OrderDisputeResolution,
)
from orders.models.orders.constants import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_DISPUTED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_SUBMITTED,
)
from orders.models.orders.order import Order


class DisputeOrchestrationService:
    """
    Own dispute lifecycle orchestration for orders.

    This service handles:
        1. Opening disputes
        2. Escalating disputes
        3. Resolving disputes
        4. Closing disputes

    This service records the dispute decision first.
    Downstream side effects such as reassignment, reopen, deadline
    extension, or refund should be delegated to specialized services.
    """

    @classmethod
    @transaction.atomic
    def open_dispute(
        cls,
        *,
        order: Order,
        opened_by: Any,
        reason: str,
        summary: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderDispute:
        """
        Open a new dispute for an eligible order.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_order_can_be_disputed(locked_order)
        cls._ensure_no_open_dispute(locked_order)
        cls._validate_actor_website(actor=opened_by, order=locked_order)

        dispute = OrderDispute.objects.create(
            website=locked_order.website,
            order=locked_order,
            opened_by=opened_by,
            reason=reason,
            summary=summary,
            status="open",
            opened_at=timezone.now(),
        )

        locked_order.status = ORDER_STATUS_DISPUTED
        locked_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_dispute_event(
            dispute=dispute,
            event_type="dispute_opened",
            actor=triggered_by or opened_by,
            metadata={
                "opened_by_id": getattr(opened_by, "pk", None),
                "reason": reason,
            },
        )
        return dispute

    @classmethod
    @transaction.atomic
    def escalate_dispute(
        cls,
        *,
        dispute: OrderDispute,
        escalated_by: Any,
        notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderDispute:
        """
        Escalate an open dispute.
        """
        locked_dispute = cls._lock_dispute(dispute)

        cls._ensure_dispute_open(locked_dispute)
        cls._validate_actor_website(
            actor=escalated_by,
            order=locked_dispute.order,
        )

        locked_dispute.status = "escalated"
        locked_dispute.escalated_at = timezone.now()
        locked_dispute.save(
            update_fields=[
                "status",
                "escalated_at",
                "updated_at",
            ]
        )

        cls._create_dispute_event(
            dispute=locked_dispute,
            event_type="dispute_escalated",
            actor=triggered_by or escalated_by,
            metadata={
                "escalated_by_id": getattr(escalated_by, "pk", None),
                "notes": notes,
            },
        )
        return locked_dispute

    @classmethod
    @transaction.atomic
    def resolve_dispute(
        cls,
        *,
        dispute: OrderDispute,
        resolved_by: Any,
        outcome: str,
        resolution_summary: str,
        internal_notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderDisputeResolution:
        """
        Resolve a dispute and persist the decision record.

        This only records the resolution. Downstream effects should be
        handled by dedicated services based on the recorded outcome.
        """
        locked_dispute = cls._lock_dispute(dispute)
        locked_order = cls._lock_order(locked_dispute.order)

        cls._ensure_dispute_resolvable(locked_dispute)
        cls._validate_actor_website(actor=resolved_by, order=locked_order)

        resolution = OrderDisputeResolution.objects.create(
            website=locked_order.website,
            dispute=locked_dispute,
            resolved_by=resolved_by,
            outcome=outcome,
            summary=resolution_summary,
            internal_notes=internal_notes,
            resolved_at=timezone.now(),
        )

        locked_dispute.status = "resolved"
        locked_dispute.resolved_at = resolution.resolved_at
        locked_dispute.save(
            update_fields=[
                "status",
                "resolved_at",
                "updated_at",
            ]
        )

        cls._create_dispute_event(
            dispute=locked_dispute,
            event_type="dispute_resolved",
            actor=triggered_by or resolved_by,
            metadata={
                "resolution_id": resolution.pk,
                "outcome": outcome,
            },
        )
        return resolution

    @classmethod
    @transaction.atomic
    def close_dispute(
        cls,
        *,
        dispute: OrderDispute,
        closed_by: Any,
        restore_order_status: str,
        triggered_by: Optional[Any] = None,
    ) -> OrderDispute:
        """
        Close a resolved dispute and restore the order to an allowed state.
        """
        locked_dispute = cls._lock_dispute(dispute)
        locked_order = cls._lock_order(locked_dispute.order)

        cls._ensure_dispute_closed_allowed(locked_dispute)
        cls._validate_actor_website(actor=closed_by, order=locked_order)
        cls._ensure_allowed_restore_status(restore_order_status)

        locked_dispute.status = "closed"
        locked_dispute.closed_at = timezone.now()
        locked_dispute.save(
            update_fields=[
                "status",
                "closed_at",
                "updated_at",
            ]
        )

        locked_order.status = restore_order_status
        locked_order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        cls._create_dispute_event(
            dispute=locked_dispute,
            event_type="dispute_closed",
            actor=triggered_by or closed_by,
            metadata={
                "closed_by_id": getattr(closed_by, "pk", None),
                "restored_order_status": restore_order_status,
            },
        )
        return locked_dispute

    @classmethod
    def _ensure_order_can_be_disputed(cls, order: Order) -> None:
        """
        Ensure an order is in a state eligible for dispute opening.
        """
        allowed_statuses = {
            ORDER_STATUS_IN_PROGRESS,
            ORDER_STATUS_SUBMITTED,
            ORDER_STATUS_COMPLETED,
        }
        if order.status not in allowed_statuses:
            raise ValidationError(
                "Only in progress, submitted, or completed orders "
                "can be disputed."
            )

    @classmethod
    def _ensure_no_open_dispute(cls, order: Order) -> None:
        """
        Ensure there is no active dispute for the order.
        """
        active_exists = (
            OrderDispute.objects.select_for_update()
            .filter(
                order=order,
                status__in=["open", "escalated", "resolved"],
            )
            .exists()
        )
        if active_exists:
            raise ValidationError(
                "Order already has an active dispute."
            )

    @classmethod
    def _ensure_dispute_open(cls, dispute: OrderDispute) -> None:
        """
        Ensure the dispute is currently open.
        """
        if dispute.status != "open":
            raise ValidationError(
                "Only open disputes can be escalated."
            )

    @classmethod
    def _ensure_dispute_resolvable(cls, dispute: OrderDispute) -> None:
        """
        Ensure the dispute can be resolved.
        """
        if dispute.status not in {"open", "escalated"}:
            raise ValidationError(
                "Only open or escalated disputes can be resolved."
            )

    @classmethod
    def _ensure_dispute_closed_allowed(cls, dispute: OrderDispute) -> None:
        """
        Ensure the dispute can be closed.
        """
        if dispute.status != "resolved":
            raise ValidationError(
                "Only resolved disputes can be closed."
            )

    @classmethod
    def _ensure_allowed_restore_status(cls, status: str) -> None:
        """
        Ensure restored order status is allowed after dispute closure.
        """
        allowed_statuses = {
            ORDER_STATUS_IN_PROGRESS,
            ORDER_STATUS_SUBMITTED,
            ORDER_STATUS_COMPLETED,
        }
        if status not in allowed_statuses:
            raise ValidationError(
                "Invalid restore order status after dispute closure."
            )

    @classmethod
    def _validate_actor_website(
        cls,
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
    def _lock_order(cls, order: Order) -> Order:
        """
        Lock and reload an order inside a transaction.
        """
        return Order.objects.select_for_update().get(pk=order.pk)

    @classmethod
    def _lock_dispute(cls, dispute: OrderDispute) -> OrderDispute:
        """
        Lock and reload a dispute inside a transaction.
        """
        return OrderDispute.objects.select_for_update().get(
            pk=dispute.pk
        )

    @classmethod
    def _create_dispute_event(
        cls,
        *,
        dispute: OrderDispute,
        event_type: str,
        actor: Optional[Any],
        metadata: dict,
    ) -> OrderDisputeEvent:
        """
        Create a dispute event.
        """
        return OrderDisputeEvent.objects.create(
            website=dispute.website,
            dispute=dispute,
            event_type=event_type,
            actor=actor,
            metadata=metadata,
        )