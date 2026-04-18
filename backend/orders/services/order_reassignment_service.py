from __future__ import annotations

from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from orders.models.orders.order import Order
from orders.models.orders.order_assignment import OrderAssignment

from orders.models.orders.order_timeline_event import OrderTimelineEvent


from orders.models.orders.constants import (
    ORDER_ASSIGNMENT_SOURCE_REASSIGNMENT,
    ORDER_ASSIGNMENT_STATUS_ACTIVE,
    ORDER_ASSIGNMENT_STATUS_RELEASED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_TIMELINE_EVENT_REASSIGNED,
    ORDER_TIMELINE_EVENT_RETURNED_TO_POOL,
    ORDER_VISIBILITY_HIDDEN,
    ORDER_VISIBILITY_POOL,
    PREFERRED_WRITER_STATUS_FALLBACK_TO_POOL,
    PREFERRED_WRITER_STATUS_NOT_REQUESTED,
    ORDER_TIMELINE_EVENT_REASSIGNMENT_REQUESTED,
    ORDER_TIMELINE_EVENT_REASSIGNMENT_REJECTED,
    ORDER_TIMELINE_EVENT_REASSIGNMENT_CANCELLED,
)
from orders.models.orders.order_reassignment_request import (
    OrderReassignmentDecision,
    OrderReassignmentRequestStatus,
    OrderReassignmentRequest,
)


class OrderReassignmentService:
    """
    Own reassignment request workflow for orders.

    This service handles:
        1. Creating reassignment requests
        2. Rejecting reassignment requests
        3. Approving return to pool
        4. Approving direct reassignment to a writer

    This service does not handle:
        1. General staffing entry routing
        2. Hold and resume
        3. Submission and completion
        4. Disputes
    """

    @classmethod
    @transaction.atomic
    def request_reassignment(
        cls,
        *,
        order: Order,
        requested_by: Any,
        requester_role: str,
        reason: str,
        internal_notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderReassignmentRequest:
        """
        Create a reassignment request for the current active assignment.
        """
        locked_order = cls._lock_order(order)

        cls._ensure_order_can_be_reassigned(locked_order)
        cls._ensure_no_pending_request(locked_order)
        cls._validate_actor_website(actor=requested_by, order=locked_order)

        current_assignment = cls._get_current_assignment(locked_order)
        if current_assignment is None:
            raise ValidationError(
                "A current assignment is required for reassignment."
            )

        request = OrderReassignmentRequest.objects.create(
            website=locked_order.website,
            order=locked_order,
            requested_by=requested_by,
            requester_role=requester_role,
            current_assignment=current_assignment,
            status=OrderReassignmentRequestStatus.PENDING,
            reason=reason,
            internal_notes=internal_notes,
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_REASSIGNMENT_REQUESTED,
            actor=triggered_by or requested_by,
            metadata={
                "reassignment_request_id": request.pk,
                "current_assignment_id": current_assignment.pk,
                "requested_by_id": getattr(requested_by, "pk", None),
                "requester_role": requester_role,
            },
        )
        return request

    @classmethod
    @transaction.atomic
    def reject_reassignment(
        cls,
        *,
        reassignment_request: OrderReassignmentRequest,
        reviewed_by: Any,
        internal_notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderReassignmentRequest:
        """
        Reject a pending reassignment request.
        """
        locked_request = cls._lock_request(reassignment_request)

        cls._ensure_pending_request(locked_request)
        cls._validate_actor_website(
            actor=reviewed_by,
            order=locked_request.order,
        )

        locked_request.status = OrderReassignmentRequestStatus.REJECTED
        locked_request.reviewed_by = reviewed_by
        locked_request.reviewed_at = timezone.now()
        if internal_notes:
            locked_request.internal_notes = internal_notes
        locked_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "internal_notes",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_request.order,
            event_type=ORDER_TIMELINE_EVENT_REASSIGNMENT_REJECTED,
            actor=triggered_by or reviewed_by,
            metadata={
                "reassignment_request_id": locked_request.pk,
                "reviewed_by_id": getattr(reviewed_by, "pk", None),
            },
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def cancel_reassignment_request(
        cls,
        *,
        reassignment_request: OrderReassignmentRequest,
        cancelled_by: Any,
        triggered_by: Optional[Any] = None,
    ) -> OrderReassignmentRequest:
        """
        Cancel a pending reassignment request.
        Used by a writer who sent a requet but has since changed their mind.
        """
        locked_request = cls._lock_request(reassignment_request)

        cls._ensure_pending_request(locked_request)

        if locked_request.requested_by != cancelled_by:
            raise ValidationError(
                "Only the requester can cancel this reassignment request."
            )

        locked_request.status = OrderReassignmentRequestStatus.CANCELLED
        locked_request.cancelled_at = timezone.now()
        locked_request.save(
            update_fields=[
                "status",
                "cancelled_at",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_request.order,
            event_type=ORDER_TIMELINE_EVENT_REASSIGNMENT_CANCELLED,
            actor=triggered_by or cancelled_by,
            metadata={
                "reassignment_request_id": locked_request.pk,
                "cancelled_by_id": getattr(cancelled_by, "pk", None),
            },
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def approve_return_to_pool(
        cls,
        *,
        reassignment_request: OrderReassignmentRequest,
        reviewed_by: Any,
        internal_notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Approve a reassignment request and return the order to the pool.
        """
        locked_request = cls._lock_request(reassignment_request)
        locked_order = cls._lock_order(locked_request.order)

        cls._ensure_pending_request(locked_request)
        cls._validate_actor_website(actor=reviewed_by, order=locked_order)

        current_assignment = cls._get_current_assignment(locked_order)
        if current_assignment is None:
            raise ValidationError(
                "A current assignment is required for reassignment."
            )

        current_assignment.status = ORDER_ASSIGNMENT_STATUS_RELEASED
        current_assignment.is_current = False
        current_assignment.released_at = timezone.now()
        current_assignment.release_reason = locked_request.reason
        current_assignment.save(
            update_fields=[
                "status",
                "is_current",
                "released_at",
                "release_reason",
                "updated_at",
            ]
        )

        locked_request.status = OrderReassignmentRequestStatus.APPROVED
        locked_request.reviewed_by = reviewed_by
        locked_request.reviewed_at = timezone.now()
        locked_request.decision = (
            OrderReassignmentDecision.RETURN_TO_POOL
        )
        if internal_notes:
            locked_request.internal_notes = internal_notes
        locked_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "decision",
                "internal_notes",
                "updated_at",
            ]
        )

        locked_order.status = ORDER_STATUS_READY_FOR_STAFFING
        locked_order.visibility_mode = ORDER_VISIBILITY_POOL
        if locked_order.preferred_writer is None:
            locked_order.preferred_writer_status = (
                PREFERRED_WRITER_STATUS_NOT_REQUESTED
            )
        else:
            locked_order.preferred_writer_status = (
                PREFERRED_WRITER_STATUS_FALLBACK_TO_POOL
            )
        locked_order.save(
            update_fields=[
                "status",
                "visibility_mode",
                "preferred_writer_status",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_REASSIGNED,
            actor=triggered_by or reviewed_by,
            metadata={
                "reassignment_request_id": locked_request.pk,
                "released_assignment_id": current_assignment.pk,
                "released_writer_id": getattr(
                    current_assignment.writer,
                    "pk",
                    None,
                ),
                "decision": OrderReassignmentDecision.RETURN_TO_POOL,
            },
        )
        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_RETURNED_TO_POOL,
            actor=triggered_by or reviewed_by,
            metadata={
                "reassignment_request_id": locked_request.pk,
                "reason": locked_request.reason,
            },
        )
        return locked_order

    @classmethod
    @transaction.atomic
    def approve_assign_specific_writer(
        cls,
        *,
        reassignment_request: OrderReassignmentRequest,
        reviewed_by: Any,
        assign_to_writer: Any,
        internal_notes: str = "",
        triggered_by: Optional[Any] = None,
    ) -> OrderAssignment:
        """
        Approve a reassignment request and assign to a specific writer.
        """
        locked_request = cls._lock_request(reassignment_request)
        locked_order = cls._lock_order(locked_request.order)

        cls._ensure_pending_request(locked_request)
        cls._validate_actor_website(actor=reviewed_by, order=locked_order)
        cls._validate_actor_website(
            actor=assign_to_writer,
            order=locked_order,
        )

        current_assignment = cls._get_current_assignment(locked_order)
        if current_assignment is None:
            raise ValidationError(
                "A current assignment is required for reassignment."
            )

        current_assignment.status = ORDER_ASSIGNMENT_STATUS_RELEASED
        current_assignment.is_current = False
        current_assignment.released_at = timezone.now()
        current_assignment.release_reason = locked_request.reason
        current_assignment.save(
            update_fields=[
                "status",
                "is_current",
                "released_at",
                "release_reason",
                "updated_at",
            ]
        )

        replacement_assignment = OrderAssignment.objects.create(
            website=locked_order.website,
            order=locked_order,
            writer=assign_to_writer,
            assigned_by=reviewed_by,
            source=ORDER_ASSIGNMENT_SOURCE_REASSIGNMENT,
            status=ORDER_ASSIGNMENT_STATUS_ACTIVE,
            is_current=True,
            source_interest=None,
        )

        locked_request.status = OrderReassignmentRequestStatus.APPROVED
        locked_request.reviewed_by = reviewed_by
        locked_request.reviewed_at = timezone.now()
        locked_request.decision = (
            OrderReassignmentDecision.ASSIGN_SPECIFIC_WRITER
        )
        locked_request.assign_to_writer = assign_to_writer
        if internal_notes:
            locked_request.internal_notes = internal_notes
        locked_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "decision",
                "assign_to_writer",
                "internal_notes",
                "updated_at",
            ]
        )

        locked_order.status = ORDER_STATUS_IN_PROGRESS
        locked_order.visibility_mode = ORDER_VISIBILITY_HIDDEN
        locked_order.save(
            update_fields=[
                "status",
                "visibility_mode",
                "updated_at",
            ]
        )

        cls._create_timeline_event(
            order=locked_order,
            event_type=ORDER_TIMELINE_EVENT_REASSIGNED,
            actor=triggered_by or reviewed_by,
            metadata={
                "reassignment_request_id": locked_request.pk,
                "released_assignment_id": current_assignment.pk,
                "replacement_assignment_id": replacement_assignment.pk,
                "replacement_writer_id": getattr(
                    assign_to_writer,
                    "pk",
                    None,
                ),
                "decision": (
                    OrderReassignmentDecision.ASSIGN_SPECIFIC_WRITER
                ),
            },
        )
        return replacement_assignment

    @classmethod
    def _ensure_order_can_be_reassigned(cls, order: Order) -> None:
        """
        Ensure an order is in a state that allows reassignment.
        """
        if order.status != ORDER_STATUS_IN_PROGRESS:
            raise ValidationError(
                "Only in progress orders can be reassigned."
            )

    @classmethod
    def _ensure_no_pending_request(cls, order: Order) -> None:
        """
        Ensure there is no pending reassignment request for the order.
        """
        pending_exists = (
            OrderReassignmentRequest.objects.select_for_update()
            .filter(
                order=order,
                status=OrderReassignmentRequestStatus.PENDING,
            )
            .exists()
        )
        if pending_exists:
            raise ValidationError(
                "Order already has a pending reassignment request."
            )

    @classmethod
    def _ensure_pending_request(
        cls,
        reassignment_request: OrderReassignmentRequest,
    ) -> None:
        """
        Ensure the reassignment request is pending.
        """
        if (
            reassignment_request.status
            != OrderReassignmentRequestStatus.PENDING
        ):
            raise ValidationError(
                "Only pending reassignment requests can be reviewed."
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
    def _get_current_assignment(
        cls,
        order: Order,
    ) -> Optional[OrderAssignment]:
        """
        Return the current active assignment for an order.
        """
        return (
            OrderAssignment.objects.select_for_update()
            .filter(order=order, is_current=True)
            .select_related("writer")
            .first()
        )

    @classmethod
    def _lock_order(cls, order: Order) -> Order:
        """
        Lock and reload an order inside a transaction.
        """
        return Order.objects.select_for_update().get(pk=order.pk)

    @classmethod
    def _lock_request(
        cls,
        reassignment_request: OrderReassignmentRequest,
    ) -> OrderReassignmentRequest:
        """
        Lock and reload a reassignment request inside a transaction.
        """
        return OrderReassignmentRequest.objects.select_for_update().get(
            pk=reassignment_request.pk
        )

    @classmethod
    def _create_timeline_event(
        cls,
        *,
        order: Order,
        event_type: str,
        actor: Optional[Any],
        metadata: dict,
    ) -> OrderTimelineEvent:
        """
        Create a timeline event for reassignment workflow changes.
        """
        return OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=event_type,
            actor=actor,
            metadata=metadata,
        )