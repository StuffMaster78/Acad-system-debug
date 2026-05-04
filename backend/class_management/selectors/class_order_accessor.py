from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from class_management.models import (
    ClassAccessDetail,
    ClassAssignment,
    ClassInstallmentPlan,
    ClassOrder,
    ClassPriceProposal,
    ClassScopeAssessment,
    ClassTask,
    ClassWriterCompensation,
)
from class_management.constants import (
    ClassAssignmentStatus,
    ClassProposalStatus,
)


class ClassOrderAccessor:
    """
    Safe accessor layer for ClassOrder related data.

    Use this in services instead of direct reverse relations like:

        class_order.writer_compensation
        class_order.installment_plan
        class_order.tasks
        class_order.price_proposals

    This keeps Pylance calm and makes service code explicit.
    """

    @staticmethod
    def get_pk(obj: Any) -> Any:
        """
        Return object primary key safely.
        """
        return getattr(obj, "pk", None)

    @staticmethod
    def get_related_obj(*, obj: Any, field_name: str) -> Any:
        """
        Return a related object safely.
        """
        return getattr(obj, field_name, None)

    @classmethod
    def assigned_writer(cls, *, class_order: ClassOrder) -> Any:
        """
        Return assigned writer or None.
        """
        return cls.get_related_obj(
            obj=class_order,
            field_name="assigned_writer",
        )

    @classmethod
    def assigned_writer_pk(cls, *, class_order: ClassOrder) -> Any:
        """
        Return assigned writer primary key or None.
        """
        return cls.get_pk(
            cls.assigned_writer(class_order=class_order),
        )

    @classmethod
    def client_pk(cls, *, class_order: ClassOrder) -> Any:
        """
        Return client primary key.
        """
        return cls.get_pk(class_order.client)

    @staticmethod
    def access_detail(
        *,
        class_order: ClassOrder,
    ) -> ClassAccessDetail | None:
        """
        Return class access detail if it exists.
        """
        return ClassAccessDetail.objects.filter(
            class_order=class_order,
        ).first()

    @staticmethod
    def scope_assessment(
        *,
        class_order: ClassOrder,
    ) -> ClassScopeAssessment | None:
        """
        Return class scope assessment if it exists.
        """
        return ClassScopeAssessment.objects.filter(
            class_order=class_order,
        ).first()

    @staticmethod
    def writer_compensation(
        *,
        class_order: ClassOrder,
    ) -> ClassWriterCompensation | None:
        """
        Return writer compensation if it exists.
        """
        return ClassWriterCompensation.objects.filter(
            class_order=class_order,
        ).select_related(
            "writer",
            "class_order",
        ).first()

    @staticmethod
    def installment_plan(
        *,
        class_order: ClassOrder,
    ) -> ClassInstallmentPlan | None:
        """
        Return installment plan if it exists.
        """
        return ClassInstallmentPlan.objects.filter(
            class_order=class_order,
        ).first()

    @staticmethod
    def active_assignment(
        *,
        class_order: ClassOrder,
    ) -> ClassAssignment | None:
        """
        Return active writer assignment if it exists.
        """
        return (
            ClassAssignment.objects.filter(
                class_order=class_order,
                status=ClassAssignmentStatus.ACTIVE,
            )
            .select_related("writer")
            .first()
        )

    @staticmethod
    def latest_active_proposal(
        *,
        class_order: ClassOrder,
    ) -> ClassPriceProposal | None:
        """
        Return latest proposal open for client action.
        """
        return (
            ClassPriceProposal.objects.filter(
                class_order=class_order,
                status__in=[
                    ClassProposalStatus.SENT,
                    ClassProposalStatus.COUNTERED,
                ],
            )
            .order_by("-created_at")
            .first()
        )

    @staticmethod
    def tasks(*, class_order: ClassOrder) -> QuerySet[ClassTask]:
        """
        Return all tasks for a class order.
        """
        return ClassTask.objects.filter(
            class_order=class_order,
        ).select_related(
            "assigned_writer",
            "scope_item",
        )

    @classmethod
    def unfinished_tasks_exist(cls, *, class_order: ClassOrder) -> bool:
        """
        Return whether the class has unfinished tasks.
        """
        return cls.tasks(class_order=class_order).exclude(
            status__in=[
                "completed",
                "cancelled",
            ],
        ).exists()

    @classmethod
    def has_installment_plan(cls, *, class_order: ClassOrder) -> bool:
        """
        Return whether the class has an installment plan.
        """
        return cls.installment_plan(class_order=class_order) is not None

    @classmethod
    def has_writer_compensation(cls, *, class_order: ClassOrder) -> bool:
        """
        Return whether the class has writer compensation.
        """
        return cls.writer_compensation(class_order=class_order) is not None

    @classmethod
    def has_access_detail(cls, *, class_order: ClassOrder) -> bool:
        """
        Return whether the class has access details.
        """
        return cls.access_detail(class_order=class_order) is not None