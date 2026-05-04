from __future__ import annotations

from decimal import Decimal

from class_management.exceptions import ClassPaymentError


class ClassPaymentValidator:
    @staticmethod
    def validate_payment_amount(*, class_order, amount: Decimal) -> None:
        if class_order.final_amount <= Decimal("0.00"):
            raise ClassPaymentError("Class order has no payable amount.")

        if class_order.balance_amount <= Decimal("0.00"):
            raise ClassPaymentError("Class order is already fully paid.")

        if amount <= Decimal("0.00"):
            raise ClassPaymentError("Payment amount must be positive.")

        if amount > class_order.balance_amount:
            raise ClassPaymentError(
                "Payment amount cannot exceed class balance."
            )

    @staticmethod
    def validate_installment_amount(*, amount: Decimal) -> None:
        if amount <= Decimal("0.00"):
            raise ClassPaymentError("Installment amount must be positive.")