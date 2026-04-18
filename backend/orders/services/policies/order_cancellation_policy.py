from __future__ import annotations

from django.core.exceptions import ValidationError

from orders.services.policies.order_status_transition_policy import (
    validate_status_transition,
)


class OrderCancellationPolicy:
    """
    Own cancellation eligibility rules for orders.

    Business rules:
        1. Orders may be cancelled from allowed primary statuses only.
        2. Approved orders cannot be cancelled.
        3. Archived orders cannot be cancelled because primary transition
           policy already blocks archived -> cancelled.
    """

    @classmethod
    def validate_can_cancel(
        cls,
        *,
        order,
    ) -> None:
        """
        Ensure an order is eligible for cancellation.

        Args:
            order:
                Order being cancelled.

        Raises:
            ValidationError:
                Raised when cancellation is not allowed.
        """
        validate_status_transition(
            from_status=order.status,
            to_status="cancelled",
        )

        if getattr(order, "approved_at", None) is not None:
            raise ValidationError(
                "Approved orders cannot be cancelled."
            )