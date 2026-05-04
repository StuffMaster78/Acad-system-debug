from __future__ import annotations

from django.utils import timezone

from class_management.models.class_installments import (
    ClassInstallment,
)
from class_management.models.class_order import (
    ClassOrder,
)
from class_management.models.class_scope import (
    ClassTask,
)
from class_management.models.class_access import (
    ClassTwoFactorRequest,
)

class ClassRiskMetrics:
    """
    Risk and bottleneck reporting.
    """

    @staticmethod
    def paused_classes(*, website):
        return ClassOrder.objects.filter(
            website=website,
            is_work_paused=True,
        ).select_related("client", "assigned_writer")

    @staticmethod
    def overdue_installments(*, website):
        return ClassInstallment.objects.filter(
            plan__class_order__website=website,
            status="overdue",
        ).select_related("plan", "plan__class_order")

    @staticmethod
    def overdue_tasks(*, website):
        return ClassTask.objects.filter(
            class_order__website=website,
            due_at__lt=timezone.now(),
        ).exclude(
            status__in=["completed", "cancelled"],
        ).select_related("class_order", "assigned_writer")

    @staticmethod
    def pending_two_factor_requests(*, website):
        return ClassTwoFactorRequest.objects.filter(
            class_order__website=website,
            status__in=["pending", "sent"],
        ).select_related("class_order", "requested_by")