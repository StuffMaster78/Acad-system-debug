from __future__ import annotations

from decimal import Decimal
from typing import Optional


class OrderPaymentGuard:
    """
    Payment guard queries for the orders domain.

    Used by FileDeliveryGuardService to check whether a client has an
    outstanding balance before generating a signed download URL for final
    order files.
    """

    @staticmethod
    def get_outstanding_balance(*, order) -> Optional[Decimal]:
        """
        Return the outstanding amount due on an order.

        Returns None if the balance cannot be determined (e.g. the order
        has no pricing snapshot), so the delivery guard degrades
        gracefully rather than blocking on ambiguity.
        """
        try:
            from orders.services.order_payment_application_service import (
                OrderPaymentApplicationService,
            )
            return OrderPaymentApplicationService.get_outstanding_amount(
                order=order
            )
        except Exception:
            return None
