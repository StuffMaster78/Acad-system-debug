"""
Base class for all order actions.
"""

from abc import ABC, abstractmethod


class BaseOrderAction(ABC):
    """
    Abstract base class for order actions.
    """

    def __init__(self, order_id: int, **params):
        """
        Initialize the action with the order ID and optional parameters.

        Args:
            order_id (int): ID of the order.
            **params: Additional parameters for the action.
        """
        self.order_id = order_id
        self.params = params

    @abstractmethod
    def execute(self):
        """
        Execute the action. Must be implemented by subclasses.

        Returns:
            Any: Result of the action execution.
        """
        raise NotImplementedError("You must implement the execute() method.")