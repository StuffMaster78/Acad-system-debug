"""
Dispatcher to find and execute order actions.
"""

from orders.actions.registry import get_action_class


class OrderActionDispatcher:
    """
    Dispatch and execute registered order actions.
    """

    @staticmethod
    def dispatch(action_name: str, order_id: int, **params):
        """
        Dispatch an action by name and execute it.

        Args:
            action_name (str): Registered action name.
            order_id (int): ID of the order.
            **params: Parameters passed to the action.

        Returns:
            Any: Result of the action's execute().

        Raises:
            ValueError: If action_name is not registered.
        """
        action_class = get_action_class(action_name)
        if not action_class:
            raise ValueError(f"Action '{action_name}' not found.")

        action_instance = action_class(order_id, **params)
        return action_instance.execute()