from __future__ import annotations

from typing import Any, Optional

from django.utils import timezone

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models.orders.order import Order
from orders.models.orders.order_assignment import (
    OrderAssignment,
)
from orders.services.order_approval_service import (
    OrderApprovalService,
)
from orders.services.order_monitoring_service import (
    OrderMonitoringService,
)
from orders.models.orders.constants import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_IN_PROGRESS,
)


class OrderReminderService:
    """
    Own reminder decision logic for order workflow.

    Responsibilities:
        1. Trigger writer acknowledgement reminders.
        2. Trigger approval reminders for completed orders.
        3. Trigger urgency or late order reminders for active work.

    Notes:
        1. This service decides when reminders should be sent.
        2. Actual delivery is delegated to NotificationService.
        3. Reminder logging can be added later if you want delivery audit.
    """

    WRITER_ACKNOWLEDGEMENT_GRACE_HOURS = 2

    # -------------------------
    # SENDERS
    # -------------------------


    @classmethod
    def send_writer_acknowledgement_reminder(
        cls,
        *,
        order: Order,
        writer: Any,
        triggered_by: Optional[Any] = None,
    ) -> bool:
        """
        Send a writer acknowledgement reminder if the order qualifies.

        Args:
            order:
                Order being evaluated.
            writer:
                Writer to notify.
            triggered_by:
                Optional actor or system marker.

        Returns:
            bool:
                True when a reminder was sent.
        """
        if not cls.should_send_writer_acknowledgement_reminder(
            order=order
        ):
            return False

        writer_deadline = getattr(order, "writer_deadline", None)
        writer_deadline_iso = (
            writer_deadline.isoformat()
            if writer_deadline is not None
            else None
        )

        NotificationService.notify(
            event_key="order.writer_acknowledgement_reminder",
            recipient=writer,
            website=order.website,
            context={
                "order_id": order.pk,
                "writer_deadline": writer_deadline_iso,
            },
            channels=["email", "in_app"],
            triggered_by=triggered_by,
        )
        return True

    @classmethod
    def send_approval_reminder(
        cls,
        *,
        order: Order,
        triggered_by: Optional[Any] = None,
    ) -> bool:
        """
        Send a client approval reminder for a submitted order.

        Args:
            order:
                Order being evaluated.
            triggered_by:
                Optional actor or system marker.

        Returns:
            bool:
                True when a reminder was sent.
        """
        if not cls.should_send_approval_reminder(order=order):
            return False

        client = getattr(order, "client", None)
        if client is None:
            return False

        completed_at = getattr(order, "completed_at", None)
        completed_at_iso = (
            completed_at.isoformat()
            if completed_at is not None
            else None
        )

        NotificationService.notify(
            event_key="order.approval_reminder",
            recipient=client,
            website=order.website,
            context={
                "order_id": order.pk,
                "completed_at": completed_at_iso,
            },
            triggered_by=triggered_by,
            channels=["email", "in_app"],
        )
        return True

    @classmethod
    def send_operational_writer_reminder(
        cls,
        *,
        order: Order,
        writer: Any,
        triggered_by: Optional[Any] = None,
    ) -> bool:
        """
        Send an urgency aware reminder to the writer for active work.

        Args:
            order:
                Order being evaluated.
            writer:
                Writer to notify.
            triggered_by:
                Optional actor or system marker.

        Returns:
            bool:
                True when a reminder was sent.
        """
        operational_state = OrderMonitoringService.build_operational_state(
            order=order
        )
        if operational_state.state_label not in {"critical", "late"}:
            return False

        NotificationService.notify(
            event_key="order.operational_writer_reminder",
            recipient=writer,
            website=order.website,
            context={
                "order_id": order.pk,
                "state_label": operational_state.state_label,
                "seconds_to_writer_deadline": (
                    operational_state.seconds_to_writer_deadline
                ),
            },
            channels=["email", "in_app"],
            triggered_by=triggered_by,
        )
        return True


    
    # -------------------------
    # DECISION LOGIC
    # -------------------------

    @classmethod
    def should_send_writer_acknowledgement_reminder(
        cls,
        *,
        order: Order,
    ) -> bool:
        """
        Return whether a writer acknowledgement reminder should be sent.

        Args:
            order:
                Order being evaluated.

        Returns:
            bool:
                True when the writer should be nudged to acknowledge.
        """
        if order.status != ORDER_STATUS_IN_PROGRESS:
            return False

        if getattr(order, "last_writer_acknowledged_at", None) is not None:
            return False

        assigned_at = getattr(order, "updated_at", None)
        if assigned_at is None:
            return True

        delta = timezone.now() - assigned_at
        return delta.total_seconds() >= (
            cls.WRITER_ACKNOWLEDGEMENT_GRACE_HOURS * 3600
        )

    @classmethod
    def should_send_approval_reminder(
        cls,
        *,
        order: Order,
    ) -> bool:
        """
        Return whether the order still needs an approval reminder.

        Args:
            order:
                Order being evaluated.

        Returns:
            bool:
                True when approval reminder is still relevant.
        """
        if order.status != ORDER_STATUS_COMPLETED:
             return False

        if getattr(order, "completed_at", None) is None:
            return False

        if getattr(order, "approved_at", None) is not None:
            return False

        return True

    @classmethod
    def should_auto_approve(
        cls,
        *,
        order: Order,
    ) -> bool:
        """
        Return whether the order qualifies for automatic approval.

        Args:
            order:
                Order being evaluated.

        Returns:
            bool:
                True when auto approval should happen.
        """
        return OrderApprovalService.can_auto_approve(order=order)
    

    # -------------------------
    # HELPERS
    # -------------------------

    @staticmethod
    def _get_current_assignment_time(
        *,
        order: Order,
    ):
        """
        Return the current assignment created time, if present.
        """
        current_assignment = (
            OrderAssignment.objects.filter(
                order=order,
                is_current=True,
            )
            .order_by("-created_at")
            .first()
        )
        if current_assignment is None:
            return None
        return getattr(current_assignment, "created_at", None)