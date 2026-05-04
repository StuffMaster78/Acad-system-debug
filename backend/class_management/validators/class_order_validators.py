from __future__ import annotations

from class_management.constants import ClassPaymentStatus
from class_management.exceptions import ClassOrderStateError


class ClassOrderValidator:
    @staticmethod
    def require_status(
        *,
        class_order,
        allowed: set[str],
        action: str
    ) -> None:
        if class_order.status not in allowed:
            raise ClassOrderStateError(
                f"Cannot {action} class order while status is "
                f"{class_order.status}."
            )

    @staticmethod
    def require_fully_paid(*, class_order) -> None:
        if class_order.payment_status != ClassPaymentStatus.PAID:
            raise ClassOrderStateError(
                "Cannot complete class order before full payment."
            )

    @staticmethod
    def require_no_unfinished_tasks(*, class_order) -> None:
        has_unfinished_tasks = class_order.tasks.exclude(
            status__in=[
                "completed",
                "cancelled",
            ]
        ).exists()

        if has_unfinished_tasks:
            raise ClassOrderStateError(
                "Cannot complete class order with unfinished tasks."
            )