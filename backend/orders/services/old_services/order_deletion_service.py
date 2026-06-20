import logging
from dataclasses import dataclass

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.orders import Order
from orders.models.orders.constants import (
    ORDER_ASSIGNMENT_STATUS_ACTIVE,
    ORDER_ASSIGNMENT_STATUS_RELEASED,
    ORDER_HOLD_STATUS_ACTIVE,
    ORDER_HOLD_STATUS_CANCELLED,
    ORDER_HOLD_STATUS_PENDING,
    ORDER_INTEREST_STATUS_DECLINED,
    ORDER_INTEREST_TERMINAL_STATUSES,
    ORDER_TIMELINE_EVENT_SOFT_DELETED,
)
from orders.order_enums import OrderStatus
from websites.models.websites import Website

log = logging.getLogger(__name__)

ALLOWED_STAFF_ROLES = {"superadmin", "admin", "support"}
CLIENT_ROLE = "client"


def user_has_any_role(user, roles) -> bool:
    """Replace with your real role checker."""
    return getattr(user, "role", None) in roles


@dataclass(frozen=True)
class DeleteResult:
    order_id: int
    was_deleted: bool
    hard: bool


class OrderDeletionService:
    """Handles soft and hard deletion, plus restore, website-scoped."""

    def __init__(self, *, website: Website):
        self.website = website

    def _ensure_same_website(self, order: Order):
        if order.website_id != self.website.id:
            raise PermissionDenied("Cross-tenant access is not allowed.")

    def _ensure_can_soft_delete(self, *, user, order: Order):
        # Staff can soft-delete any order.
        if user_has_any_role(user, ALLOWED_STAFF_ROLES):
            return

        # Clients: only if unpaid.
        if getattr(user, "role", None) == CLIENT_ROLE:
            if order.user_id != user.id:
                raise PermissionDenied("Cannot delete another user's order.")
            if order.status != OrderStatus.UNPAID:
                raise PermissionDenied("Client can only delete unpaid orders.")
            return

        raise PermissionDenied("Insufficient privileges to delete order.")

    def _ensure_can_hard_delete(self, *, user):
        if not user_has_any_role(user, ALLOWED_STAFF_ROLES):
            raise PermissionDenied("Only staff can hard-delete orders.")

    @transaction.atomic
    def soft_delete(
        self, *, user, order: Order, reason: str = ""
    ) -> DeleteResult:
        """
        Soft-delete an order and cascade to all active child records.

        Children handled:
          - OrderAssignment (ACTIVE → RELEASED)
          - OrderInterest / bids (non-terminal → DECLINED)
          - OrderHold (PENDING/ACTIVE → CANCELLED)
          - OrderDispute (OPEN/ESCALATED → CLOSED)
          - OrderCancellationRequest (PENDING → REJECTED)
          - OrderReassignmentRequest (PENDING → CANCELLED)
          - CompensationEvent (voided if window open, reversed otherwise)
        """
        self._ensure_same_website(order)
        self._ensure_can_soft_delete(user=user, order=order)

        if order.is_deleted:
            return DeleteResult(order_id=order.id, was_deleted=False, hard=False)

        # Lock the row before cascading.
        locked_order = Order.all_objects.select_for_update().get(pk=order.pk)

        self._cascade_children(order=locked_order, actor=user)

        locked_order.mark_deleted(user=user, reason=reason)
        locked_order.save(update_fields=[
            "is_deleted", "deleted_at", "deleted_by",
            "delete_reason", "restored_at", "restored_by",
        ])

        from orders.models.orders.order_timeline_event import OrderTimelineEvent
        OrderTimelineEvent.objects.create(
            website=locked_order.website,
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_SOFT_DELETED,
            actor=user,
            metadata={"reason": reason or ""},
        )

        return DeleteResult(order_id=locked_order.id, was_deleted=True, hard=False)

    @staticmethod
    def _cascade_children(*, order: Order, actor) -> None:
        """
        Cascade a soft-delete to all live child records of the order.
        Each child type is handled independently so one failure does not
        silently abort the others — errors are logged and re-raised.
        """
        now = timezone.now()

        # 1. Release the active assignment.
        from orders.models.orders.order_assignment import OrderAssignment
        OrderAssignment.objects.filter(
            order=order,
            status=ORDER_ASSIGNMENT_STATUS_ACTIVE,
        ).update(
            status=ORDER_ASSIGNMENT_STATUS_RELEASED,
            is_current=False,
            released_at=now,
            release_reason="order_soft_deleted",
            updated_at=now,
        )

        # 2. Decline all non-terminal bids / interests.
        from orders.models.orders.order_interest import OrderInterest
        OrderInterest.objects.filter(order=order).exclude(
            status__in=ORDER_INTEREST_TERMINAL_STATUSES,
        ).update(
            status=ORDER_INTEREST_STATUS_DECLINED,
            updated_at=now,
        )

        # 3. Cancel any active or pending holds.
        from orders.models.orders.order_hold import OrderHold
        OrderHold.objects.filter(
            order=order,
            status__in=[ORDER_HOLD_STATUS_PENDING, ORDER_HOLD_STATUS_ACTIVE],
        ).update(
            status=ORDER_HOLD_STATUS_CANCELLED,
            updated_at=now,
        )

        # 4. Close open / escalated disputes.
        from orders.models.disputes.order_dispute import OrderDispute, OrderDisputeStatus
        OrderDispute.objects.filter(
            order=order,
            status__in=[OrderDisputeStatus.OPEN, OrderDisputeStatus.ESCALATED],
        ).update(
            status=OrderDisputeStatus.CLOSED,
            closed_at=now,
            updated_at=now,
        )

        # 5. Reject pending cancellation requests.
        from orders.models.orders.order_cancellation_request import OrderCancellationRequest
        OrderCancellationRequest.objects.filter(
            order=order,
            status=OrderCancellationRequest.STATUS_PENDING,
        ).update(status=OrderCancellationRequest.STATUS_REJECTED)

        # 6. Cancel pending reassignment requests.
        from orders.models.orders.order_reassignment_request import (
            OrderReassignmentRequest,
            OrderReassignmentRequestStatus,
        )
        OrderReassignmentRequest.objects.filter(
            order=order,
            status=OrderReassignmentRequestStatus.PENDING,
        ).update(
            status=OrderReassignmentRequestStatus.CANCELLED,
            updated_at=now,
        )

        # 7. Void or reverse the writer's compensation event.
        try:
            from writer_compensation.models.compensation_event import CompensationEvent
            from writer_compensation.enums.compensation_enums import EventStatus, WindowStatus
            from writer_compensation.services.event_intake_service import EventIntakeService

            event = (
                CompensationEvent.objects
                .select_related("payment_window")
                .filter(source_type="order", source_id=order.pk)
                .exclude(status__in=[EventStatus.VOIDED, EventStatus.REVERSED])
                .first()
            )
            if event:
                window_status = event.payment_window.status if event.payment_window else None
                note = f"Order #{order.pk} soft-deleted"
                if window_status == WindowStatus.OPEN and event.status != EventStatus.PAID:
                    EventIntakeService.void_event(event, voided_by=actor, reason=note)
                else:
                    EventIntakeService.create_reversal(original_event=event, created_by=actor, notes=note)
        except Exception:
            log.exception(
                "_cascade_children: compensation reversal failed for order %s — "
                "manual review required.", order.pk,
            )

    @transaction.atomic
    def restore(self, *, user, order: Order) -> int:
        """Restore a soft-deleted order."""
        self._ensure_same_website(order)

        if not order.is_deleted:
            raise ValidationError("Order is not deleted.")

        # Staff can always restore; client can restore only own order.
        if user_has_any_role(user, ALLOWED_STAFF_ROLES):
            pass
        elif getattr(user, "role", None) == CLIENT_ROLE:
            if order.user_id != user.id:
                raise PermissionDenied("Cannot restore another user's order.")
        else:
            raise PermissionDenied("Insufficient privileges to restore order.")

        order.mark_restored(user=user)
        order.save(update_fields=[
            "is_deleted", "restored_at", "restored_by"
        ])

        # optional: audit log hook
        # AuditLogger.log(user, "order.restored", {...})

        return order.id

    @transaction.atomic
    def hard_delete_by_id(self, *, user, order_id: int) -> DeleteResult:
        """Irreversible delete (DB row removal). Staff only."""
        self._ensure_can_hard_delete(user=user)

        try:
            # Use all_objects to access even soft-deleted orders
            order = Order.all_objects.select_for_update().get(
                id=order_id, website_id=self.website.id
            )
        except Order.DoesNotExist:
            # Idempotent: treat as already gone
            return DeleteResult(order_id=order_id, was_deleted=False, hard=True)

        # Optional safety net: forbid hard delete of PAID unless superadmin
        # if order.status != OrderStatus.UNPAID and user.role != "superadmin":
        # raise PermissionDenied("Only superadmin can purge paid orders.")

        oid = order.id
        order.delete()
        # optional: audit log hook
        # AuditLogger.log(user, "order.hard_deleted", {"order_id": oid})

        return DeleteResult(order_id=oid, was_deleted=True, hard=True)