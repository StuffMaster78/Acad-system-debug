from __future__ import annotations

from django.db import transaction

from special_orders.constants import SpecialOrderStatus
from special_orders.models import SpecialOrder
from special_orders.services.new_services.special_order_state_service import (
    SpecialOrderStateService,
)


class SpecialOrderHoldService:
    """
    Put special orders on hold and release them back to a valid status.
    """

    HOLDABLE_STATUSES = {
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
    }

    @classmethod
    @transaction.atomic
    def put_on_hold(
        cls,
        *,
        special_order: SpecialOrder,
        held_by,
        reason: str,
    ) -> SpecialOrder:
        """
        Put a special order on hold.
        """
        if not reason.strip():
            raise ValueError("Hold reason is required.")

        special_order = cls._lock_order(special_order=special_order)

        if special_order.status not in cls.HOLDABLE_STATUSES:
            raise ValueError("Special order cannot be placed on hold.")

        previous_status = special_order.status

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=SpecialOrderStatus.ON_HOLD,
            changed_by=held_by,
            reason=reason,
            metadata={
                "previous_status": previous_status,
            },
        )

    @classmethod
    @transaction.atomic
    def release_hold(
        cls,
        *,
        special_order: SpecialOrder,
        released_by,
        restore_status: str,
        reason: str = "",
    ) -> SpecialOrder:
        """
        Release a held special order back to a valid status.
        """
        special_order = cls._lock_order(special_order=special_order)

        if special_order.status != SpecialOrderStatus.ON_HOLD:
            raise ValueError("Only held special orders can be released.")

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=restore_status,
            changed_by=released_by,
            reason=reason or "Special order hold released.",
            metadata={
                "restore_status": restore_status,
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