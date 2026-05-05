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


class SpecialOrderSubmissionService:
    """
    Handle writer/staff submissions for special orders.
    """

    SUBMITTABLE_STATUSES = {
        SpecialOrderStatus.IN_PROGRESS,
        SpecialOrderStatus.ON_REVISION,
    }

    @classmethod
    @transaction.atomic
    def submit_work(
        cls,
        *,
        special_order: SpecialOrder,
        submitted_by,
        notes: str = "",
        mark_ready_for_delivery: bool = False,
    ) -> SpecialOrder:
        """
        Submit work for review or final delivery.
        """
        special_order = cls._lock_order(special_order=special_order)

        cls._validate_submitter(
            special_order=special_order,
            submitted_by=submitted_by,
        )
        cls._validate_submittable(special_order=special_order)

        SpecialOrderCompletionLog.objects.create(
            website=special_order.website,
            special_order=special_order,
            completed_by=submitted_by,
            action="work_submitted",
            justification=notes,
            metadata={
                "mark_ready_for_delivery": mark_ready_for_delivery,
            },
        )

        next_status = SpecialOrderStatus.SUBMITTED

        if mark_ready_for_delivery:
            SpecialOrderDeliveryGuardService.assert_can_deliver_final(
                special_order=special_order,
            )
            next_status = SpecialOrderStatus.READY_FOR_DELIVERY

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=next_status,
            changed_by=submitted_by,
            reason=notes or "Special order work submitted.",
            metadata={
                "submitted_at": timezone.now().isoformat(),
            },
        )

    @classmethod
    @transaction.atomic
    def mark_ready_for_delivery(
        cls,
        *,
        special_order: SpecialOrder,
        marked_by,
        notes: str = "",
    ) -> SpecialOrder:
        """
        Mark a submitted special order as ready for delivery.
        """
        special_order = cls._lock_order(special_order=special_order)

        if special_order.status != SpecialOrderStatus.SUBMITTED:
            raise ValueError(
                "Only submitted special orders can be marked ready "
                "for delivery."
            )

        SpecialOrderDeliveryGuardService.assert_can_deliver_final(
            special_order=special_order,
        )

        SpecialOrderCompletionLog.objects.create(
            website=special_order.website,
            special_order=special_order,
            completed_by=marked_by,
            action="ready_for_delivery",
            justification=notes,
        )

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=SpecialOrderStatus.READY_FOR_DELIVERY,
            changed_by=marked_by,
            reason=notes or "Special order is ready for delivery.",
        )

    @staticmethod
    def _lock_order(*, special_order: SpecialOrder) -> SpecialOrder:
        return SpecialOrder.objects.select_for_update().get(
            id=special_order.id,
            website=special_order.website,
        )

    @classmethod
    def _validate_submittable(
        cls,
        *,
        special_order: SpecialOrder,
    ) -> None:
        if special_order.status not in cls.SUBMITTABLE_STATUSES:
            raise ValueError(
                "Special order cannot be submitted in its current status."
            )

    @staticmethod
    def _validate_submitter(
        *,
        special_order: SpecialOrder,
        submitted_by,
    ) -> None:
        """
        Assigned writer or staff can submit.
        """
        role = str(getattr(submitted_by, "role", "")).lower()

        staff_roles = {
            "admin",
            "superadmin",
            "support",
            "editor",
            "content_manager",
        }

        if role in staff_roles:
            return

        if special_order.writer_id == getattr(submitted_by, "id", None):
            return

        raise PermissionError(
            "Only assigned writer or staff can submit this special order."
        )