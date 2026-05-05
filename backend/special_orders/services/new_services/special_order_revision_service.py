from __future__ import annotations

from django.db import transaction

from special_orders.constants import SpecialOrderStatus
from special_orders.models import SpecialOrder, SpecialOrderCompletionLog
from special_orders.services.new_services.special_order_state_service import (
    SpecialOrderStateService,
)


class SpecialOrderRevisionService:
    """
    Handle revision requests and revision work for special orders.

    This service does not price paid revisions. If a revision is outside the
    free revision window or changes scope, use ChangeRequestService.
    """

    REVISION_REQUESTABLE_STATUSES = {
        SpecialOrderStatus.SUBMITTED,
        SpecialOrderStatus.READY_FOR_DELIVERY,
        SpecialOrderStatus.COMPLETED,
    }

    @classmethod
    @transaction.atomic
    def request_revision(
        cls,
        *,
        special_order: SpecialOrder,
        requested_by,
        reason: str,
        metadata: dict | None = None,
    ) -> SpecialOrder:
        """
        Request a revision on submitted, ready, or completed work.
        """
        if not reason.strip():
            raise ValueError("Revision reason is required.")

        special_order = cls._lock_order(special_order=special_order)

        if special_order.status not in cls.REVISION_REQUESTABLE_STATUSES:
            raise ValueError(
                "Special order cannot receive a revision request "
                "in its current status."
            )

        SpecialOrderCompletionLog.objects.create(
            website=special_order.website,
            special_order=special_order,
            completed_by=requested_by,
            action="revision_requested",
            justification=reason,
            metadata=metadata or {},
        )

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=SpecialOrderStatus.REVISION_REQUESTED,
            changed_by=requested_by,
            reason=reason,
            metadata=metadata,
        )

    @classmethod
    @transaction.atomic
    def start_revision(
        cls,
        *,
        special_order: SpecialOrder,
        started_by,
        notes: str = "",
    ) -> SpecialOrder:
        """
        Move a revision-requested order into revision work.
        """
        special_order = cls._lock_order(special_order=special_order)

        if special_order.status != SpecialOrderStatus.REVISION_REQUESTED:
            raise ValueError(
                "Only revision-requested special orders can enter revision."
            )

        cls._validate_revision_actor(
            special_order=special_order,
            actor=started_by,
        )

        SpecialOrderCompletionLog.objects.create(
            website=special_order.website,
            special_order=special_order,
            completed_by=started_by,
            action="revision_started",
            justification=notes,
        )

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=SpecialOrderStatus.ON_REVISION,
            changed_by=started_by,
            reason=notes or "Special order revision started.",
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

    @staticmethod
    def _validate_revision_actor(
        *,
        special_order: SpecialOrder,
        actor,
    ) -> None:
        """
        Assigned writer or staff can start revision work.
        """
        role = str(getattr(actor, "role", "")).lower()

        staff_roles = {
            "admin",
            "superadmin",
            "support",
            "editor",
            "content_manager",
        }

        if role in staff_roles:
            return

        if special_order.writer_id == getattr(actor, "id", None):
            return

        raise PermissionError(
            "Only assigned writer or staff can start this revision."
        )