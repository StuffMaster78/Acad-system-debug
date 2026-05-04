from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from class_management.constants import (
    ClassTaskStatus,
    ClassTimelineEventType,
)
from class_management.exceptions import ClassManagementError
from class_management.models.class_order import (
    ClassOrder,
)
from class_management.models.class_scope import (
    ClassScopeAssessment,
    ClassScopeItem,
    ClassTask,
)
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)


class ClassScopeService:
    """
    Service for workload assessment, scope items, and class tasks.
    """

    @classmethod
    @transaction.atomic
    def create_or_update_assessment(
        cls,
        *,
        class_order: ClassOrder,
        assessed_by,
        discussion_posts_count: int = 0,
        discussion_responses_count: int = 0,
        quizzes_count: int = 0,
        exams_count: int = 0,
        assignments_count: int = 0,
        research_papers_count: int = 0,
        term_papers_count: int = 0,
        coursework_items_count: int = 0,
        projects_count: int = 0,
        presentations_count: int = 0,
        labs_count: int = 0,
        estimated_hours: Decimal = Decimal("0.00"),
        complexity_level: str = "medium",
        weekly_workload_notes: str = "",
        grading_weight_notes: str = "",
        client_scope_notes: str = "",
        admin_assessment_notes: str = "",
    ) -> ClassScopeAssessment:
        """
        Create or update the class workload assessment.
        """
        cls._validate_non_negative_counts(
            values=[
                discussion_posts_count,
                discussion_responses_count,
                quizzes_count,
                exams_count,
                assignments_count,
                research_papers_count,
                term_papers_count,
                coursework_items_count,
                projects_count,
                presentations_count,
                labs_count,
            ],
        )

        if estimated_hours < Decimal("0.00"):
            raise ClassManagementError(
                "Estimated hours cannot be negative."
            )

        assessment, _ = ClassScopeAssessment.objects.update_or_create(
            class_order=class_order,
            defaults={
                "discussion_posts_count": discussion_posts_count,
                "discussion_responses_count": discussion_responses_count,
                "quizzes_count": quizzes_count,
                "exams_count": exams_count,
                "assignments_count": assignments_count,
                "research_papers_count": research_papers_count,
                "term_papers_count": term_papers_count,
                "coursework_items_count": coursework_items_count,
                "projects_count": projects_count,
                "presentations_count": presentations_count,
                "labs_count": labs_count,
                "estimated_hours": estimated_hours,
                "complexity_level": complexity_level,
                "weekly_workload_notes": weekly_workload_notes,
                "grading_weight_notes": grading_weight_notes,
                "client_scope_notes": client_scope_notes,
                "admin_assessment_notes": admin_assessment_notes,
                "assessed_by": assessed_by,
                "assessed_at": timezone.now(),
            },
        )

        class_order.complexity_level = complexity_level
        class_order.updated_by = assessed_by
        class_order.save(
            update_fields=[
                "complexity_level",
                "updated_by",
                "updated_at",
            ],
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.REVIEW_STARTED,
            title="Class scope assessed",
            triggered_by=assessed_by,
            metadata={
                "assessment_id": assessment.pk,
                "estimated_hours": str(estimated_hours),
                "complexity_level": complexity_level,
            },
        )

        return assessment

    @classmethod
    @transaction.atomic
    def add_scope_item(
        cls,
        *,
        class_order: ClassOrder,
        item_type: str,
        title: str,
        created_by,
        quantity: int = 1,
        due_at=None,
        estimated_pages: int | None = None,
        estimated_words: int | None = None,
        estimated_hours: Decimal | None = None,
        complexity_level: str = "medium",
        notes: str = "",
    ) -> ClassScopeItem:
        """
        Add a workload item to a class order.
        """
        if quantity <= 0:
            raise ClassManagementError(
                "Scope item quantity must be greater than zero."
            )

        if estimated_hours is not None and estimated_hours < Decimal("0.00"):
            raise ClassManagementError(
                "Estimated hours cannot be negative."
            )

        scope_item = ClassScopeItem.objects.create(
            class_order=class_order,
            item_type=item_type,
            title=title,
            quantity=quantity,
            due_at=due_at,
            estimated_pages=estimated_pages,
            estimated_words=estimated_words,
            estimated_hours=estimated_hours,
            complexity_level=complexity_level,
            notes=notes,
            created_by=created_by,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.TASK_CREATED,
            title="Class scope item added",
            triggered_by=created_by,
            metadata={
                "scope_item_id": scope_item.pk,
                "item_type": item_type,
                "quantity": quantity,
            },
        )

        return scope_item

    @classmethod
    @transaction.atomic
    def create_task_from_scope_item(
        cls,
        *,
        scope_item: ClassScopeItem,
        created_by,
        title: str = "",
        description: str = "",
        assigned_writer=None,
        due_at=None,
    ) -> ClassTask:
        """
        Create an actionable task from a scope item.
        """
        class_order = scope_item.class_order
        writer = assigned_writer or cls._get_related_obj(
            obj=class_order,
            field_name="assigned_writer",
        )

        task = ClassTask.objects.create(
            class_order=class_order,
            scope_item=scope_item,
            assigned_writer=writer,
            title=title or scope_item.title,
            description=description or scope_item.notes,
            due_at=due_at or scope_item.due_at,
            created_by=created_by,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.TASK_CREATED,
            title="Class task created",
            triggered_by=created_by,
            metadata={
                "task_id": task.pk,
                "scope_item_id": scope_item.pk,
            },
        )

        return task

    @classmethod
    @transaction.atomic
    def create_manual_task(
        cls,
        *,
        class_order: ClassOrder,
        title: str,
        created_by,
        description: str = "",
        assigned_writer=None,
        due_at=None,
        client_visible_notes: str = "",
        writer_notes: str = "",
        admin_internal_notes: str = "",
        portal_flags: dict[str, Any] | None = None,
    ) -> ClassTask:
        """
        Create an ad hoc class task not tied to a scope item.
        """
        writer = assigned_writer or cls._get_related_obj(
            obj=class_order,
            field_name="assigned_writer",
        )

        task = ClassTask.objects.create(
            class_order=class_order,
            assigned_writer=writer,
            title=title,
            description=description,
            due_at=due_at,
            client_visible_notes=client_visible_notes,
            writer_notes=writer_notes,
            admin_internal_notes=admin_internal_notes,
            created_by=created_by,
        )

        if portal_flags:
            cls.apply_portal_flags(
                task=task,
                flags=portal_flags,
            )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.TASK_CREATED,
            title="Class task created",
            triggered_by=created_by,
            metadata={"task_id": task.pk},
        )

        return task

    @classmethod
    @transaction.atomic
    def start_task(
        cls,
        *,
        task: ClassTask,
        started_by,
    ) -> ClassTask:
        """
        Mark a class task as in progress.
        """
        if task.status not in {
            ClassTaskStatus.PENDING,
            ClassTaskStatus.ASSIGNED,
        }:
            raise ClassManagementError(
                "Only pending or assigned tasks can be started."
            )

        task.status = ClassTaskStatus.IN_PROGRESS
        task.started_at = timezone.now()
        task.save(
            update_fields=[
                "status",
                "started_at",
                "updated_at",
            ],
        )

        return task

    @classmethod
    @transaction.atomic
    def submit_task(
        cls,
        *,
        task: ClassTask,
        submitted_by,
        notes: str = "",
        portal_submitted: bool = False,
    ) -> ClassTask:
        """
        Mark a class task as submitted.
        """
        if task.status not in {
            ClassTaskStatus.IN_PROGRESS,
            ClassTaskStatus.ASSIGNED,
        }:
            raise ClassManagementError(
                "Only assigned or in-progress tasks can be submitted."
            )

        task.status = ClassTaskStatus.SUBMITTED
        task.submitted_at = timezone.now()

        if notes:
            task.writer_notes = (
                f"{task.writer_notes}\n{notes}"
            ).strip()

        update_fields = [
            "status",
            "submitted_at",
            "writer_notes",
            "updated_at",
        ]

        if hasattr(task, "portal_submitted_at") and portal_submitted:
            task.portal_submitted_at = timezone.now()
            update_fields.append("portal_submitted_at")

        task.save(update_fields=update_fields)

        ClassTimelineService.record(
            class_order=task.class_order,
            event_type=ClassTimelineEventType.TASK_COMPLETED,
            title="Class task submitted",
            description=notes,
            triggered_by=submitted_by,
            metadata={"task_id": task.pk},
        )

        return task

    @classmethod
    @transaction.atomic
    def complete_task(
        cls,
        *,
        task: ClassTask,
        completed_by,
        notes: str = "",
    ) -> ClassTask:
        """
        Mark a class task completed.
        """
        if task.status not in {
            ClassTaskStatus.SUBMITTED,
            ClassTaskStatus.IN_PROGRESS,
            ClassTaskStatus.ASSIGNED,
        }:
            raise ClassManagementError(
                "Only active or submitted tasks can be completed."
            )

        task.status = ClassTaskStatus.COMPLETED
        task.completed_at = timezone.now()

        if notes:
            task.admin_internal_notes = (
                f"{task.admin_internal_notes}\n{notes}"
            ).strip()

        task.save(
            update_fields=[
                "status",
                "completed_at",
                "admin_internal_notes",
                "updated_at",
            ],
        )

        ClassTimelineService.record(
            class_order=task.class_order,
            event_type=ClassTimelineEventType.TASK_COMPLETED,
            title="Class task completed",
            description=notes,
            triggered_by=completed_by,
            metadata={"task_id": task.pk},
        )

        return task

    @classmethod
    @transaction.atomic
    def cancel_task(
        cls,
        *,
        task: ClassTask,
        cancelled_by,
        reason: str,
    ) -> ClassTask:
        """
        Cancel a class task.
        """
        if task.status == ClassTaskStatus.COMPLETED:
            raise ClassManagementError(
                "Completed class tasks cannot be cancelled."
            )

        task.status = ClassTaskStatus.CANCELLED
        task.admin_internal_notes = (
            f"{task.admin_internal_notes}\n"
            f"Cancellation reason: {reason}"
        ).strip()
        task.save(
            update_fields=[
                "status",
                "admin_internal_notes",
                "updated_at",
            ],
        )

        ClassTimelineService.record(
            class_order=task.class_order,
            event_type=ClassTimelineEventType.TASK_COMPLETED,
            title="Class task cancelled",
            description=reason,
            triggered_by=cancelled_by,
            metadata={"task_id": task.pk},
        )

        return task

    @staticmethod
    def apply_portal_flags(
        *,
        task: ClassTask,
        flags: dict[str, Any],
    ) -> None:
        """
        Apply portal workflow flags if the fields exist on ClassTask.
        """
        allowed_fields = {
            "requires_portal_work",
            "writer_may_upload_to_portal",
            "writer_may_download_files",
            "portal_submission_required",
            "portal_submission_notes",
        }

        update_fields = []

        for field_name, value in flags.items():
            if field_name in allowed_fields and hasattr(task, field_name):
                setattr(task, field_name, value)
                update_fields.append(field_name)

        if update_fields:
            update_fields.append("updated_at")
            task.save(update_fields=update_fields)

    @staticmethod
    def _validate_non_negative_counts(
        *,
        values: list[int],
    ) -> None:
        """
        Ensure count values are not negative.
        """
        if any(value < 0 for value in values):
            raise ClassManagementError(
                "Scope count values cannot be negative."
            )

    @staticmethod
    def _get_related_obj(*, obj: Any, field_name: str) -> Any:
        """
        Return a related object safely.
        """
        return getattr(obj, field_name, None)