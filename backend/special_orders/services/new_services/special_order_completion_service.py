from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from special_orders.constants import SpecialOrderStatus
from special_orders.models import (
    SpecialOrder,
    SpecialOrderCompletionLog,
)
from special_orders.services.new_services.special_order_delivery_guard_service import (
    SpecialOrderDeliveryGuardService,
)
from special_orders.services.new_services.special_order_state_service import (
    SpecialOrderStateService,
)


class SpecialOrderCompletionService:
    """
    Complete and approve special orders.

    Completion means the work has been delivered or accepted as complete.
    Approval is a stronger final state after client/staff confirmation.
    """

    COMPLETABLE_STATUSES = {
        SpecialOrderStatus.READY_FOR_DELIVERY,
        SpecialOrderStatus.SUBMITTED,
    }

    APPROVABLE_STATUSES = {
        SpecialOrderStatus.COMPLETED,
    }

    @classmethod
    @transaction.atomic
    def complete_order(
        cls,
        *,
        special_order: SpecialOrder,
        completed_by,
        notes: str = "",
    ) -> SpecialOrder:
        """
        Mark a special order as completed.
        """
        special_order = cls._lock_order(special_order=special_order)

        cls._validate_completable(special_order=special_order)

        SpecialOrderDeliveryGuardService.assert_can_deliver_final(
            special_order=special_order,
        )

        completed_at = timezone.now()
        special_order.completed_at = completed_at
        special_order.save(
            update_fields=[
                "completed_at",
                "updated_at",
            ]
        )

        SpecialOrderCompletionLog.objects.create(
            website=special_order.website,
            special_order=special_order,
            completed_by=completed_by,
            action="completed",
            justification=notes,
            metadata={
                "completed_at": completed_at.isoformat(),
            },
        )

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=SpecialOrderStatus.COMPLETED,
            changed_by=completed_by,
            reason=notes or "Special order completed.",
        )

    @classmethod
    @transaction.atomic
    def approve_order(
        cls,
        *,
        special_order: SpecialOrder,
        approved_by,
        notes: str = "",
    ) -> SpecialOrder:
        """
        Mark a completed special order as approved.
        """
        special_order = cls._lock_order(special_order=special_order)

        if special_order.status not in cls.APPROVABLE_STATUSES:
            raise ValueError("Only completed special orders can be approved.")

        SpecialOrderCompletionLog.objects.create(
            website=special_order.website,
            special_order=special_order,
            completed_by=approved_by,
            action="approved",
            justification=notes,
        )

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=SpecialOrderStatus.APPROVED,
            changed_by=approved_by,
            reason=notes or "Special order approved.",
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

    @classmethod
    def _validate_completable(
        cls,
        *,
        special_order: SpecialOrder,
    ) -> None:
        """
        Validate completion status.
        """
        if special_order.status not in cls.COMPLETABLE_STATUSES:
            raise ValueError(
                "Special order cannot be completed in its current status."
            )