from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from special_orders.constants import SpecialOrderStatus
from special_orders.models import SpecialOrder, SpecialOrderWriterPayRule
from special_orders.services.new_services.special_order_state_service import (
    SpecialOrderStateService,
)
from special_orders.services.new_services.special_order_delivery_guard_service import (
    SpecialOrderDeliveryGuardService,
)
from communications.constants import CommunicationThreadKind
from communications.models.thread import CommunicationThread
from communications.services.participant_sync_service import (
    CommunicationParticipantSyncService,
)



class SpecialOrderAssignmentService:
    """
    Assign writers to special orders.

    This service only handles assignment. It does not create writer earnings,
    bonuses, wallet records, or ledger entries.
    """

    ASSIGNABLE_STATUSES = {
        SpecialOrderStatus.READY_FOR_STAFFING,
        SpecialOrderStatus.ASSIGNED,
    }

    @classmethod
    @transaction.atomic
    def assign_writer(
        cls,
        *,
        special_order: SpecialOrder,
        writer,
        assigned_by=None,
        writer_pay_rule: SpecialOrderWriterPayRule | None = None,
        reason: str = "",
    ) -> SpecialOrder:
        """
        Assign or reassign a writer to a special order.
        """
        special_order = cls._lock_order(special_order=special_order)

        cls._validate_assignable(special_order=special_order)
        cls._validate_writer(
            special_order=special_order,
            writer=writer,
        )
        cls._validate_writer_pay_rule(
            special_order=special_order,
            writer_pay_rule=writer_pay_rule,
        )

        special_order.writer = writer
        special_order.writer_pay_rule_id = (
            writer_pay_rule.id if writer_pay_rule is not None else None
        )
        special_order.assigned_at = timezone.now()
        special_order.save(
            update_fields=[
                "writer",
                "writer_pay_rule_id",
                "assigned_at",
                "updated_at",
            ]
        )

        if special_order.status != SpecialOrderStatus.ASSIGNED:
            special_order = SpecialOrderStateService.transition(
                special_order=special_order,
                to_status=SpecialOrderStatus.ASSIGNED,
                changed_by=assigned_by,
                reason=reason or "Writer assigned to special order.",
                metadata={
                    "writer_id": writer.id,
                    "writer_pay_rule_id": (
                        writer_pay_rule.id if writer_pay_rule else None
                    ),
                },
            )



        return special_order

    @staticmethod
    def sync_special_order_writer_communications(
        *,
        special_order,
        new_writer,
        old_writer=None,
        actor=None,
    ) -> None:
        content_type = ContentType.objects.get_for_model(special_order)

        threads = CommunicationThread.objects.filter(
            website=special_order.website,
            target_content_type=content_type,
            target_object_id=special_order.pk,
            kind__in=[
                CommunicationThreadKind.CLIENT_WRITER,
                CommunicationThreadKind.WRITER_SUPPORT,
            ],
        )

        transaction.on_commit(
            lambda: CommunicationParticipantSyncService.sync_writer(
                threads=threads,
                new_writer=new_writer,
                old_writer=old_writer,
                actor=actor,
            ),
        )

    @classmethod
    @transaction.atomic
    def start_work(
        cls,
        *,
        special_order: SpecialOrder,
        started_by=None,
        reason: str = "",
    ) -> SpecialOrder:
        """
        Move an assigned special order into progress.
        """
        special_order = cls._lock_order(special_order=special_order)

        if special_order.status != SpecialOrderStatus.ASSIGNED:
            raise ValueError("Only assigned special orders can be started.")

        if special_order.writer_id is None:
            raise ValueError("Special order has no assigned writer.")

        special_order.started_at = timezone.now()
        special_order.save(
            update_fields=[
                "started_at",
                "updated_at",
            ]
        )

        SpecialOrderDeliveryGuardService.assert_can_start_work(
            special_order=special_order,
        )

        return SpecialOrderStateService.transition(
            special_order=special_order,
            to_status=SpecialOrderStatus.IN_PROGRESS,
            changed_by=started_by,
            reason=reason or "Special order work started.",
            metadata={
                "writer_id": special_order.writer_id,
            },
        )

    @staticmethod
    def _lock_order(*, special_order: SpecialOrder) -> SpecialOrder:
        """
        Lock special order row for safe assignment.
        """
        return SpecialOrder.objects.select_for_update().get(
            id=special_order.id,
            website=special_order.website,
        )

    @classmethod
    def _validate_assignable(
        cls,
        *,
        special_order: SpecialOrder,
    ) -> None:
        """
        Ensure the special order can receive a writer.
        """
        if special_order.status not in cls.ASSIGNABLE_STATUSES:
            raise ValueError(
                "Special order is not ready for writer assignment."
            )

    @staticmethod
    def _validate_writer(
        *,
        special_order: SpecialOrder,
        writer,
    ) -> None:
        """
        Validate writer belongs to same tenant and has writer role.
        """
        if getattr(writer, "website_id", None) != special_order.website_id:
            raise ValueError("Writer belongs to another tenant.")

        if str(getattr(writer, "role", "")).lower() != "writer":
            raise ValueError("Assigned user must be a writer.")

    @staticmethod
    def _validate_writer_pay_rule(
        *,
        special_order: SpecialOrder,
        writer_pay_rule: SpecialOrderWriterPayRule | None,
    ) -> None:
        """
        Validate writer pay rule belongs to same tenant.
        """
        if writer_pay_rule is None:
            return

        if writer_pay_rule.website.id != special_order.website_id:
            raise ValueError("Writer pay rule belongs to another tenant.")

        if not writer_pay_rule.is_active:
            raise ValueError("Writer pay rule is inactive.")