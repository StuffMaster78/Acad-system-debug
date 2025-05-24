"""
Service for evaluating and applying flags to an Order instance.
"""

from typing import List
from datetime import timedelta

from django.utils import timezone

from orders.order_enums import OrderFlags
from orders.models import Order  # Adjust path as needed
from users.models import User


class OrderFlagsService:
    """
    Service to determine and apply appropriate flags to an Order instance.
    """

    HIGH_VALUE_THRESHOLD = 300  # USD
    URGENT_THRESHOLD_HOURS = 24

    def __init__(self, order: Order):
        self.order = order
        self.client: User = order.client

    def evaluate_flags(self) -> List[OrderFlags]:
        """
        Evaluates which flags should apply to this order.
        """
        flags = []

        if self._is_urgent():
            flags.append(OrderFlags.URGENT_ORDER)

        if self._is_first_order():
            flags.append(OrderFlags.FIRST_CLIENT_ORDER)
        elif self._is_returning_client():
            flags.append(OrderFlags.RETURNING_CLIENT_ORDER)

        if self._is_high_value():
            flags.append(OrderFlags.HIGH_VALUE_ORDER)

        if self._is_preferred_order():
            flags.append(OrderFlags.PREFERRED_ORDER)

        return flags

    def apply_flags(self, persist: bool = True) -> List[OrderFlags]:
        """
        Applies all appropriate flags to the order.
        """
        flags = self.evaluate_flags()
        self.order.flags = [flag.value for flag in flags]
        if persist:
            self.order.save(update_fields=["flags"])
        return flags

    def _is_urgent(self) -> bool:
        """
        Check if the order is urgent (deadline < 24 hours from now).
        """
        return (self.order.deadline - timezone.now()) < timedelta(
            hours=self.URGENT_THRESHOLD_HOURS
        )

    def _is_first_order(self) -> bool:
        """
        Check if this is the client's first order.
        """
        return not Order.objects.filter(client=self.client).exclude(id=self.order.id).exists()

    def _is_returning_client(self) -> bool:
        """
        Check if this is not the first order (i.e., returning).
        """
        return Order.objects.filter(client=self.client).exclude(id=self.order.id).exists()

    def _is_high_value(self) -> bool:
        """
        Check if order is considered high value.
        """
        return self.order.total_price >= self.HIGH_VALUE_THRESHOLD

    def _is_preferred_order(self) -> bool:
        """
        Placeholder: could be based on writer preference, client reputation, etc.
        """
        return getattr(self.client, "is_preferred", False)