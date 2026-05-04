# class_management/services/class_portal_work_log_service.py

from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from class_management.constants import (
    ClassPortalActivityType,
    ClassPortalWorkLogVerificationStatus,
    ClassTimelineEventType,
)
from class_management.exceptions import ClassManagementError
from class_management.models import (
    ClassOrder,
    ClassPortalWorkLog,
    ClassTask,
)
from class_management.services.class_communication_service import (
    ClassCommunicationService,
)
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)
from notifications_system.services.notification_service import (
    NotificationService,
)


class ClassPortalWorkLogService:
    """
    Manage writer-reported class portal activity logs.

    Class work happens inside an external school portal. This service creates
    an internal audit trail so admins, clients, and writers can track what was
    done without storing unsafe portal details in messages.
    """

    @classmethod
    @transaction.atomic
    def log_activity(
        cls,
        *,
        class_order: ClassOrder,
        writer,
        activity_type: str,
        title: str,
        occurred_at,
        task: ClassTask | None = None,
        description: str = "",
        portal_reference: str = "",
        visible_to_client: bool = True,
        post_to_thread: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> ClassPortalWorkLog:
        """
        Record writer-reported work completed in the school portal.

        Only the assigned writer may log activity for a class. When requested,
        a safe progress update is also posted into the central communications
        thread.
        """
        cls._validate_writer_can_log(
            class_order=class_order,
            writer=writer,
        )
        cls._validate_task_belongs_to_order(
            class_order=class_order,
            task=task,
        )

        work_log = ClassPortalWorkLog.objects.create(
            class_order=class_order,
            task=task,
            writer=writer,
            activity_type=activity_type,
            title=title,
            description=description,
            portal_reference=portal_reference,
            occurred_at=occurred_at,
            visible_to_client=visible_to_client,
            metadata=metadata or {},
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.TASK_COMPLETED,
            title="Portal activity logged",
            description=title,
            triggered_by=writer,
            metadata={
                "portal_work_log_id": cls._get_pk(work_log),
                "activity_type": activity_type,
                "task_id": cls._get_pk(task),
            },
        )

        if post_to_thread and visible_to_client:
            cls._post_safe_progress_message(
                class_order=class_order,
                writer=writer,
                work_log=work_log,
            )

        NotificationService.notify(
            event_key="class.portal_work_logged",
            recipient=class_order.client,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
                "activity_title": work_log.title,
                "activity_type": work_log.activity_type,
            },
            triggered_by=writer,
            is_silent=not visible_to_client,
        )

        return work_log

    @classmethod
    @transaction.atomic
    def verify_log(
        cls,
        *,
        work_log: ClassPortalWorkLog,
        verified_by,
        notes: str = "",
    ) -> ClassPortalWorkLog:
        """
        Mark a portal activity log as admin verified.
        """
        work_log.verification_status = (
            ClassPortalWorkLogVerificationStatus.VERIFIED
        )
        work_log.verified_by = verified_by
        work_log.verified_at = timezone.now()
        work_log.verification_notes = notes
        work_log.save(
            update_fields=[
                "verification_status",
                "verified_by",
                "verified_at",
                "verification_notes",
            ],
        )

        ClassTimelineService.record(
            class_order=work_log.class_order,
            event_type=ClassTimelineEventType.TASK_COMPLETED,
            title="Portal activity verified",
            description=notes,
            triggered_by=verified_by,
            metadata={
                "portal_work_log_id": cls._get_pk(work_log),
            },
        )

        return work_log

    @classmethod
    @transaction.atomic
    def reject_log(
        cls,
        *,
        work_log: ClassPortalWorkLog,
        rejected_by,
        notes: str,
    ) -> ClassPortalWorkLog:
        """
        Reject a portal activity log after admin review.
        """
        work_log.verification_status = (
            ClassPortalWorkLogVerificationStatus.REJECTED
        )
        work_log.verified_by = rejected_by
        work_log.verified_at = timezone.now()
        work_log.verification_notes = notes
        work_log.save(
            update_fields=[
                "verification_status",
                "verified_by",
                "verified_at",
                "verification_notes",
            ],
        )

        ClassTimelineService.record(
            class_order=work_log.class_order,
            event_type=ClassTimelineEventType.TASK_COMPLETED,
            title="Portal activity rejected",
            description=notes,
            triggered_by=rejected_by,
            metadata={
                "portal_work_log_id": cls._get_pk(work_log),
            },
        )

        return work_log

    @classmethod
    def _post_safe_progress_message(
        cls,
        *,
        class_order: ClassOrder,
        writer,
        work_log: ClassPortalWorkLog,
    ) -> None:
        """
        Post a safe progress update to the class communication thread.

        The message must not include credentials, grades, hidden admin notes,
        private portal details, or any off-platform contact information.
        """
        activity_label = cls._get_activity_label(work_log.activity_type)
        reference = work_log.portal_reference or "N/A"

        message = (
            f"Progress update: {work_log.title}\n\n"
            f"Activity: {activity_label}\n"
            f"Reference: {reference}"
        )

        ClassCommunicationService.send_message(
            class_order=class_order,
            sender=writer,
            recipient=class_order.client,
            sender_role="writer",
            recipient_role="client",
            message=message,
            metadata={
                "source": "class_portal_work_log",
                "portal_work_log_id": cls._get_pk(work_log),
                "activity_type": work_log.activity_type,
            },
        )

    @classmethod
    def _validate_writer_can_log(
        cls,
        *,
        class_order: ClassOrder,
        writer,
    ) -> None:
        """
        Ensure only the assigned writer can log portal activity.
        """
        assigned_writer_pk = cls._get_related_pk(
            obj=class_order,
            field_name="assigned_writer",
        )
        writer_pk = cls._get_pk(writer)

        if assigned_writer_pk != writer_pk:
            raise ClassManagementError(
                "Only the assigned writer can log portal activity."
            )

    @classmethod
    def _validate_task_belongs_to_order(
        cls,
        *,
        class_order: ClassOrder,
        task: ClassTask | None,
    ) -> None:
        """
        Ensure a provided task belongs to the same class order.
        """
        if task is None:
            return

        task_order_pk = cls._get_related_pk(
            obj=task,
            field_name="class_order",
        )

        if task_order_pk != class_order.pk:
            raise ClassManagementError(
                "Task does not belong to this class order."
            )

    @staticmethod
    def _get_related_pk(*, obj: Any, field_name: str) -> Any:
        """
        Return the primary key for a related object safely.
        """
        related_obj = getattr(obj, field_name, None)
        return getattr(related_obj, "pk", None)

    @staticmethod
    def _get_pk(obj: Any) -> Any:
        """
        Return an object's primary key safely.
        """
        return getattr(obj, "pk", None)

    @staticmethod
    def _get_activity_label(activity_type: str) -> str:
        """
        Return the display label for a portal activity type.
        """
        for value, label in ClassPortalActivityType.choices:
            if value == activity_type:
                return str(label)

        return activity_type