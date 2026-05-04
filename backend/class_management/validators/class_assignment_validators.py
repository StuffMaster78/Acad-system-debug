from __future__ import annotations

from class_management.exceptions import ClassAssignmentError


class ClassAssignmentValidator:
    @staticmethod
    def require_assignable_status(
        *,
        class_order,
        allowed_statuses: set[str],
    ) -> None:
        if class_order.status not in allowed_statuses:
            raise ClassAssignmentError(
                "Cannot assign writer while class order status is "
                f"{class_order.status}."
            )

    @staticmethod
    def require_no_active_assignment(*, active_assignment) -> None:
        if active_assignment:
            raise ClassAssignmentError(
                "This class order already has an active writer."
            )

    @staticmethod
    def require_active_assignment(*, assignment) -> None:
        if assignment is None:
            raise ClassAssignmentError(
                "This class order has no active writer."
            )