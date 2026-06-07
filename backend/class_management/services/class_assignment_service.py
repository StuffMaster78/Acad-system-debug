from __future__ import annotations


from typing import Any
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from class_management.constants import (
    ClassAssignmentStatus,
    ClassOrderStatus,
    ClassPaymentStatus,
    ClassTimelineEventType,
)
from class_management.exceptions import ClassAssignmentError
from class_management.models import ClassAssignment, ClassOrder
from class_management.services.class_communication_service import (
    ClassCommunicationService,
)
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)
from class_management.state_machine import ClassOrderStateMachine
from notifications_system.services.notification_service import (
    NotificationService,
)
from communications.constants import CommunicationThreadKind
from communications.models.thread import CommunicationThread
from communications.services.participant_sync_service import (
    CommunicationParticipantSyncService,
)



class ClassAssignmentService:
    """
    Service for assigning, reassigning, and removing class writers.
    """

    ASSIGN_ALLOWED_STATUSES = {
        ClassOrderStatus.PAID,
        ClassOrderStatus.ASSIGNED,
        ClassOrderStatus.IN_PROGRESS,
    }

    @classmethod
    @transaction.atomic
    def assign_writer(
        cls,
        *,
        class_order: ClassOrder,
        writer,
        assigned_by,
        assignment_notes: str = "",
        writer_visible_notes: str = "",
    ) -> ClassAssignment:
        """
        Assign a writer to a class order.
        """
        cls._ensure_order_can_be_assigned(class_order=class_order)

        if cls.get_active_assignment(class_order=class_order):
            raise ClassAssignmentError(
                "This class order already has an active writer."
            )

        assignment = ClassAssignment.objects.create(
            class_order=class_order,
            writer=writer,
            assigned_by=assigned_by,
            assignment_notes=assignment_notes,
        )

        class_order.assigned_writer = writer
        class_order.updated_by = assigned_by

        if writer_visible_notes:
            class_order.writer_visible_notes = writer_visible_notes

        class_order.save(
            update_fields=[
                "assigned_writer",
                "writer_visible_notes",
                "updated_by",
                "updated_at",
            ],
        )

        if ClassOrderStateMachine.can_transition(
            from_status=class_order.status,
            to_status=ClassOrderStatus.ASSIGNED,
        ):
            ClassOrderStateMachine.transition(
                class_order=class_order,
                to_status=ClassOrderStatus.ASSIGNED,
                triggered_by=assigned_by,
                metadata={
                    "writer_id": cls._get_pk(writer),
                    "assignment_id": cls._get_pk(assignment),
                },
            )

        ClassCommunicationService.sync_participants(
            class_order=class_order,
        )

        cls.sync_class_writer_communications(
            class_order=class_order,
            new_writer=writer,
            old_writer=None,
            actor=assigned_by,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.WRITER_ASSIGNED,
            title="Class writer assigned",
            description=assignment_notes,
            triggered_by=assigned_by,
            metadata={
                "writer_id": cls._get_pk(writer),
                "assignment_id": cls._get_pk(assignment),
            },
        )

        NotificationService.notify(
            event_key="class.writer_assigned",
            recipient=writer,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
            },
            triggered_by=assigned_by,
        )

        return assignment

    @classmethod
    @transaction.atomic
    def reassign_writer(
        cls,
        *,
        class_order: ClassOrder,
        new_writer,
        reassigned_by,
        reason: str,
        assignment_notes: str = "",
    ) -> ClassAssignment:
        """
        Replace the active class writer.
        """
        old_assignment = cls.get_active_assignment(
            class_order=class_order,
        )
        old_writer = old_assignment.writer if old_assignment else None

        if old_assignment:
            old_assignment.status = ClassAssignmentStatus.REASSIGNED
            old_assignment.removal_reason = reason
            old_assignment.removed_at = timezone.now()
            old_assignment.save(
                update_fields=[
                    "status",
                    "removal_reason",
                    "removed_at",
                ],
            )

        assignment = ClassAssignment.objects.create(
            class_order=class_order,
            writer=new_writer,
            assigned_by=reassigned_by,
            assignment_notes=assignment_notes,
        )

        class_order.assigned_writer = new_writer
        class_order.updated_by = reassigned_by
        class_order.save(
            update_fields=[
                "assigned_writer",
                "updated_by",
                "updated_at",
            ],
        )

        ClassCommunicationService.sync_participants(
            class_order=class_order,
        )

        cls.sync_class_writer_communications(
            class_order=class_order,
            new_writer=new_writer,
            old_writer=old_writer,
            actor=reassigned_by,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.WRITER_ASSIGNED,
            title="Class writer reassigned",
            description=reason,
            triggered_by=reassigned_by,
            metadata={
                "new_writer_id": cls._get_pk(new_writer),
                "assignment_id": cls._get_pk(assignment),
            },
        )

        NotificationService.notify(
            event_key="class.writer_assigned",
            recipient=new_writer,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
            },
            triggered_by=reassigned_by,
        )

        return assignment

    @staticmethod
    def sync_class_writer_communications(
        *,
        class_order: ClassOrder,
        new_writer=None,
        old_writer=None,
        actor=None,
    ) -> None:
        content_type = ContentType.objects.get_for_model(class_order)

        threads = CommunicationThread.objects.filter(
            website=class_order.website,
            target_content_type=content_type,
            target_object_id=class_order.pk,
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
    def remove_writer(
        cls,
        *,
        class_order: ClassOrder,
        removed_by,
        reason: str,
    ) -> None:
        """
        Remove the active writer from a class order.
        """
        assignment = cls.get_active_assignment(
            class_order=class_order,
        )

        if assignment is None:
            raise ClassAssignmentError(
                "This class order has no active writer."
            )

        assignment.status = ClassAssignmentStatus.REMOVED
        assignment.removal_reason = reason
        assignment.removed_at = timezone.now()
        assignment.save(
            update_fields=[
                "status",
                "removal_reason",
                "removed_at",
            ],
        )

        class_order.assigned_writer = None
        class_order.updated_by = removed_by
        class_order.save(
            update_fields=[
                "assigned_writer",
                "updated_by",
                "updated_at",
            ],
        )
        cls.sync_class_writer_communications(
            class_order=class_order,
            new_writer=None,
            old_writer=assignment.writer,
            actor=removed_by,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.WRITER_ASSIGNED,
            title="Class writer removed",
            description=reason,
            triggered_by=removed_by,
            metadata={
                "assignment_id": cls._get_pk(assignment),
                "writer_id": cls._get_related_pk(
                    obj=assignment,
                    field_name="writer",
                ),
            },
        )

    @staticmethod
    def get_active_assignment(
        *,
        class_order: ClassOrder,
    ) -> ClassAssignment | None:
        """
        Return the active assignment for a class order.
        """
        return (
            ClassAssignment.objects.filter(
                class_order=class_order,
                status=ClassAssignmentStatus.ACTIVE,
            )
            .select_related("writer")
            .first()
        )

    @classmethod
    def _ensure_order_can_be_assigned(
        cls,
        *,
        class_order: ClassOrder,
    ) -> None:
        """
        Validate class order status before writer assignment.
        """
        if class_order.status not in cls.ASSIGN_ALLOWED_STATUSES:
            raise ClassAssignmentError(
                "Cannot assign writer while class order status is "
                f"{class_order.status}."
            )
        if class_order.payment_status != ClassPaymentStatus.PAID:
            raise ClassAssignmentError(
                "Cannot assign writer before the class order is fully paid."
            )

    @staticmethod
    def _get_pk(obj: Any) -> Any:
        """
        Return an object's primary key safely.
        """
        return getattr(obj, "pk", None)

    @staticmethod
    def _get_related_pk(*, obj: Any, field_name: str) -> Any:
        """
        Return a related object's primary key safely.
        """
        related_obj = getattr(obj, field_name, None)
        return getattr(related_obj, "pk", None)
