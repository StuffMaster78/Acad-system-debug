from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.orders.constants import (
    ORDER_ASSIGNMENT_STATUS_RELEASED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_TIMELINE_EVENT_ASSIGNED,
    ORDER_TIMELINE_EVENT_ASSIGNMENT_ACCEPTED,
    ORDER_TIMELINE_EVENT_ASSIGNMENT_REJECTED,
    ORDER_VISIBILITY_HIDDEN,
)
from orders.models.orders.enums import OrderStatus
from orders.models.orders.order_direct_assignment import OrderDirectAssignment
from orders.models.orders.order_timeline_event import OrderTimelineEvent
from orders.services.staffing.order_staffing_store import OrderStaffingStore


class OrderAssignmentAcceptanceService:
    """
    Manage the acceptance gate for staff-direct assignments.

    When staff assigns a writer directly, the order parks in
    pending_writer_acceptance. This service drives the accept/reject
    transitions.
    """

    @classmethod
    @transaction.atomic
    def create_acceptance_gate(
        cls,
        *,
        order,
        writer: Any,
        assigned_by: Any,
        assignment,
    ) -> OrderDirectAssignment:
        order.status = OrderStatus.PENDING_WRITER_ACCEPTANCE
        order.visibility_mode = ORDER_VISIBILITY_HIDDEN
        order.save(update_fields=["status", "visibility_mode", "updated_at"])

        gate = OrderDirectAssignment.objects.create(
            website=order.website,
            order=order,
            writer=writer,
            assigned_by=assigned_by,
            status=OrderDirectAssignment.STATUS_PENDING,
        )

        OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=ORDER_TIMELINE_EVENT_ASSIGNED,
            actor=assigned_by,
            metadata={
                "assignment_id": assignment.pk,
                "writer_id": getattr(writer, "pk", None),
                "gate_id": gate.pk,
                "pending_acceptance": True,
            },
        )
        return gate

    @classmethod
    @transaction.atomic
    def accept(
        cls,
        *,
        gate: OrderDirectAssignment,
        writer: Any,
        reason: str = "",
    ) -> OrderDirectAssignment:
        if gate.status != OrderDirectAssignment.STATUS_PENDING:
            raise ValidationError(
                f"Cannot accept: gate is already {gate.status}."
            )
        if getattr(writer, "pk", None) != gate.writer_id:
            raise ValidationError("Only the assigned writer can accept.")

        gate.status = OrderDirectAssignment.STATUS_ACCEPTED
        gate.reason = reason
        gate.responded_at = timezone.now()
        gate.save(update_fields=["status", "reason", "responded_at"])

        order = gate.order
        order.status = ORDER_STATUS_IN_PROGRESS
        order.save(update_fields=["status", "updated_at"])

        OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=ORDER_TIMELINE_EVENT_ASSIGNMENT_ACCEPTED,
            actor=writer,
            metadata={
                "gate_id": gate.pk,
                "assigned_by_id": gate.assigned_by_id,
                "reason": reason,
            },
        )

        cls._notify_assignment_accepted(gate=gate)
        return gate

    @classmethod
    @transaction.atomic
    def reject(
        cls,
        *,
        gate: OrderDirectAssignment,
        writer: Any,
        reason: str = "",
    ) -> OrderDirectAssignment:
        if gate.status != OrderDirectAssignment.STATUS_PENDING:
            raise ValidationError(
                f"Cannot reject: gate is already {gate.status}."
            )
        if getattr(writer, "pk", None) != gate.writer_id:
            raise ValidationError("Only the assigned writer can reject.")

        gate.status = OrderDirectAssignment.STATUS_REJECTED
        gate.reason = reason
        gate.responded_at = timezone.now()
        gate.save(update_fields=["status", "reason", "responded_at"])

        order = gate.order

        # Release the OrderAssignment record
        current_assignment = OrderStaffingStore.get_current_assignment(order=order)
        if current_assignment is not None:
            current_assignment.status = ORDER_ASSIGNMENT_STATUS_RELEASED
            current_assignment.is_current = False
            current_assignment.released_at = timezone.now()
            current_assignment.release_reason = f"writer_rejected:{reason}"
            current_assignment.save(
                update_fields=[
                    "status",
                    "is_current",
                    "released_at",
                    "release_reason",
                    "updated_at",
                ]
            )

        order.status = ORDER_STATUS_READY_FOR_STAFFING
        order.save(update_fields=["status", "updated_at"])

        OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            event_type=ORDER_TIMELINE_EVENT_ASSIGNMENT_REJECTED,
            actor=writer,
            metadata={
                "gate_id": gate.pk,
                "assigned_by_id": gate.assigned_by_id,
                "reason": reason,
            },
        )

        cls._notify_assignment_rejected(gate=gate, reason=reason)
        return gate

    @staticmethod
    def _notify_assignment_accepted(*, gate: OrderDirectAssignment) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            if gate.assigned_by_id:
                NotificationService.notify(
                    event_key="order.assignment_accepted",
                    recipient=gate.assigned_by,
                    website=gate.website,
                    context={
                        "order_id": gate.order_id,
                        "writer_id": gate.writer_id,
                    },
                    channels={"in_app": True, "email": True},
                    triggered_by=gate.writer,
                    priority="high",
                    is_broadcast=False,
                    is_digest=False,
                    is_silent=False,
                    digest_group=None,
                )
        except Exception:
            import logging
            logging.getLogger(__name__).warning(
                "Failed to send assignment_accepted notification gate_id=%s",
                gate.pk,
                exc_info=True,
            )

    @staticmethod
    def _notify_assignment_rejected(
        *, gate: OrderDirectAssignment, reason: str
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            if gate.assigned_by_id:
                NotificationService.notify(
                    event_key="order.assignment_rejected",
                    recipient=gate.assigned_by,
                    website=gate.website,
                    context={
                        "order_id": gate.order_id,
                        "writer_id": gate.writer_id,
                        "reason": reason,
                    },
                    channels={"in_app": True, "email": True},
                    triggered_by=gate.writer,
                    priority="high",
                    is_broadcast=False,
                    is_digest=False,
                    is_silent=False,
                    digest_group=None,
                )
        except Exception:
            import logging
            logging.getLogger(__name__).warning(
                "Failed to send assignment_rejected notification gate_id=%s",
                gate.pk,
                exc_info=True,
            )
