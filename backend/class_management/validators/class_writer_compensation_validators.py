from __future__ import annotations

from decimal import Decimal

from class_management.exceptions import ClassWriterCompensationError


class ClassWriterCompensationValidator:
    @staticmethod
    def require_assigned_writer(*, class_order, writer) -> None:
        if not class_order.assigned_writer_id:
            raise ClassWriterCompensationError(
                "Assign a writer before setting compensation."
            )

        if class_order.assigned_writer_id != writer.id:
            raise ClassWriterCompensationError(
                "Compensation writer must match assigned writer."
            )

    @staticmethod
    def validate_percentage(*, percentage: Decimal | None) -> None:
        if percentage is None or percentage <= Decimal("0.00"):
            raise ClassWriterCompensationError(
                "Percentage compensation requires a positive percentage."
            )

        if percentage > Decimal("100.00"):
            raise ClassWriterCompensationError(
                "Percentage cannot exceed 100."
            )

    @staticmethod
    def validate_fixed_amount(
        *,
        fixed_amount: Decimal | None,
        class_amount: Decimal,
    ) -> None:
        if fixed_amount is None or fixed_amount <= Decimal("0.00"):
            raise ClassWriterCompensationError(
                "Fixed compensation requires a positive amount."
            )

        if fixed_amount > class_amount:
            raise ClassWriterCompensationError(
                "Writer compensation cannot exceed class amount."
            )