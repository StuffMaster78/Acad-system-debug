from __future__ import annotations

from django.utils import timezone

from class_management.selectors import ClassPaymentSelector
from class_management.services.class_installment_service import (
    ClassInstallmentService,
)


def mark_overdue_installments():
    """
    Find overdue installments and mark them overdue.
    Optionally pause work.
    """
    now = timezone.now()

    installments = ClassPaymentSelector.overdue_installments(
        website=None,  # loop per tenant later if needed
    )

    for installment in installments:
        if installment.due_at and installment.due_at <= now:
            ClassInstallmentService.mark_overdue_installments()


def auto_pause_work_for_overdue():
    """
    Pause class work if configured and overdue exists.
    """
    installments = ClassPaymentSelector.overdue_installments(
        website=None,
    )

    for installment in installments:
        plan = installment.plan
        class_order = plan.class_order

        if not plan.pause_work_when_overdue:
            continue

        if class_order.is_work_paused:
            continue

        ClassInstallmentService.pause_work_for_overdue_installment(
            class_order=class_order,
        )