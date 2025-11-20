"""
Base class for all order actions.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from django.apps import apps

class BaseOrderAction(ABC):
    """
    Abstract base class for order actions.
    """

    def __init__(self, order_id: int, user=None, **params: Any):
        """
        Initialize the action with the order ID and optional parameters.

        Args:
            order_id (int): ID of the order.
            **params: Additional parameters for the action.
        """
        self.order_id = order_id
        self.user = user

        # lazy model fetch to avoid circular imports
        Order = apps.get_model("orders", "Order")
        self.order = Order.objects.select_related("website").get(pk=order_id)
        self.params = params

    @abstractmethod
    def execute(self):
        """
        Execute the action. Must be implemented by subclasses.

        Returns:
            Any: Result of the action execution.
        """
        raise NotImplementedError("You must implement the execute() method.")
    