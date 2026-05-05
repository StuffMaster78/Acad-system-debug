from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from special_orders.constants import SpecialOrderStatus
from special_orders.models import (
    SpecialOrder,
    SpecialOrderStatusHistory,
)


class SpecialOrderStateService:
    """
    Central authority for SpecialOrder status transitions.

    No other service should mutate `special_order.status` directly.
    """

    # Allowed transitions map
    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        SpecialOrderStatus.INQUIRY: {
            SpecialOrderStatus.QUOTE_PENDING,
            SpecialOrderStatus.AWAITING_PAYMENT,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.QUOTE_PENDING: {
            SpecialOrderStatus.QUOTE_SENT,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.QUOTE_SENT: {
            SpecialOrderStatus.QUOTE_ACCEPTED,
            SpecialOrderStatus.QUOTE_PENDING,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.QUOTE_ACCEPTED: {
            SpecialOrderStatus.AWAITING_PAYMENT,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.AWAITING_PAYMENT: {
            SpecialOrderStatus.PARTIALLY_FUNDED,
            SpecialOrderStatus.READY_FOR_STAFFING,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.REFUNDED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.PARTIALLY_FUNDED: {
            SpecialOrderStatus.READY_FOR_STAFFING,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.REFUNDED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.READY_FOR_STAFFING: {
            SpecialOrderStatus.ASSIGNED,
            SpecialOrderStatus.IN_PROGRESS,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.REFUNDED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.ASSIGNED: {
            SpecialOrderStatus.IN_PROGRESS,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.IN_PROGRESS: {
            SpecialOrderStatus.SUBMITTED,
            SpecialOrderStatus.READY_FOR_DELIVERY,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.SUBMITTED: {
            SpecialOrderStatus.READY_FOR_DELIVERY,
            SpecialOrderStatus.COMPLETED,
            SpecialOrderStatus.REVISION_REQUESTED,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.READY_FOR_DELIVERY: {
            SpecialOrderStatus.COMPLETED,
            SpecialOrderStatus.REVISION_REQUESTED,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.COMPLETED: {
            SpecialOrderStatus.APPROVED,
            SpecialOrderStatus.REVISION_REQUESTED,
            SpecialOrderStatus.REFUNDED,
        },
        SpecialOrderStatus.APPROVED: {
            SpecialOrderStatus.REFUNDED,
        },
        SpecialOrderStatus.REVISION_REQUESTED: {
            SpecialOrderStatus.ON_REVISION,
            SpecialOrderStatus.CANCELLED,
        },
        SpecialOrderStatus.ON_REVISION: {
            SpecialOrderStatus.SUBMITTED,
            SpecialOrderStatus.READY_FOR_DELIVERY,
            SpecialOrderStatus.CANCELLED,
            SpecialOrderStatus.ON_HOLD,
        },
        SpecialOrderStatus.ON_HOLD: {
            SpecialOrderStatus.INQUIRY,
            SpecialOrderStatus.QUOTE_PENDING,
            SpecialOrderStatus.QUOTE_SENT,
            SpecialOrderStatus.QUOTE_ACCEPTED,
            SpecialOrderStatus.AWAITING_PAYMENT,
            SpecialOrderStatus.PARTIALLY_FUNDED,
            SpecialOrderStatus.READY_FOR_STAFFING,
            SpecialOrderStatus.ASSIGNED,
            SpecialOrderStatus.IN_PROGRESS,
            SpecialOrderStatus.SUBMITTED,
            SpecialOrderStatus.READY_FOR_DELIVERY,
            SpecialOrderStatus.ON_REVISION,
            SpecialOrderStatus.CANCELLED,
        },
        SpecialOrderStatus.CANCELLED: set(),
        SpecialOrderStatus.REFUNDED: set(),
    }

    @classmethod
    @transaction.atomic
    def transition(
        cls,
        *,
        special_order: SpecialOrder,
        to_status: str,
        changed_by=None,
        reason: str = "",
        metadata: dict | None = None,
    ) -> SpecialOrder:
        """
        Perform a safe state transition.
        """
        special_order = cls._lock_order(special_order)

        from_status = special_order.status

        cls._validate_transition(
            from_status=from_status,
            to_status=to_status,
        )

        if from_status == to_status:
            return special_order

        special_order.status = to_status
        special_order.save(update_fields=["status", "updated_at"])

        cls._record_history(
            special_order=special_order,
            from_status=from_status,
            to_status=to_status,
            changed_by=changed_by,
            reason=reason,
            metadata=metadata,
        )

        return special_order

    @staticmethod
    def _lock_order(
        special_order: SpecialOrder,
    ) -> SpecialOrder:
        """
        Lock order row to avoid race conditions.
        """
        return SpecialOrder.objects.select_for_update().get(
            id=special_order.id,
            website=special_order.website,
        )

    @classmethod
    def _validate_transition(
        cls,
        *,
        from_status: str,
        to_status: str,
    ) -> None:
        """
        Ensure transition is allowed.
        """
        allowed = cls.ALLOWED_TRANSITIONS.get(from_status, set())

        if to_status not in allowed:
            raise ValueError(
                f"Invalid status transition: {from_status} -> {to_status}"
            )

    @staticmethod
    def _record_history(
        *,
        special_order: SpecialOrder,
        from_status: str,
        to_status: str,
        changed_by=None,
        reason: str = "",
        metadata: dict | None = None,
    ) -> None:
        """
        Persist audit trail.
        """
        SpecialOrderStatusHistory.objects.create(
            website=special_order.website,
            special_order=special_order,
            previous_status=from_status,
            new_status=to_status,
            reason=reason,
            changed_by=changed_by,
            metadata=metadata or {},
        )