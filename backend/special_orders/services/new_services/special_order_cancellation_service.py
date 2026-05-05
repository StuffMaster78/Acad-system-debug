from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from special_orders.constants import SpecialOrderStatus
from special_orders.models import SpecialOrder
from special_orders.services.new_services.special_order_state_service import (
    SpecialOrderStateService,
)


class SpecialOrderCancellationService:
    """
    Cancel special orders.

    Refunds are not performed here. If money has moved, call refund
    services separately after cancellation decision.
    """

    CANCELLABLE_STATUSES = {
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
        SpecialOrderStatus.ON_HOLD,
    }

    @classmethod
    @transaction.atomic
    def cancel_order(
        cls,
        *,
        special_order: SpecialOrder,
        cancelled_by,
        reason: str,
    ) -> SpecialOrder:
        """
        Cancel a special order.
        """
        if not reason.strip():
            raise ValueError("Cancellation reason is required.")

        special_order = cls._lock_order(special_order=special_order)

        if special_order.status not in cls.CANCELLABLE_STATUSES:
            raise ValueError("Special order cannot be cancelled.")

        cancelled_at = timezone.now()
        special_order.cancelled_at = cancelled_at
        special_order.save(
            update_fields=[
                "cancelled_at",
                "updated_at",
            ]
        )

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=SpecialOrderStatus.CANCELLED,
            changed_by=cancelled_by,
            reason=reason,
            metadata={
                "cancelled_at": cancelled_at.isoformat(),
            },
        )

    @staticmethod
    def _lock_order(*, special_order: SpecialOrder) -> SpecialOrder:
        """
        Lock special order row.
        """
        return SpecialOrder.objects.select_for_update().get(
            id=special_order.id,
            website=special_order.website,
        )