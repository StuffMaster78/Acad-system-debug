from orders.models import Order
from django_fsm import TransitionNotAllowed # type: ignore


class OrderActionHandler:
    """
    Base class for handling order actions.
    Each order action (e.g., transition, assign, complete) is a subclass of this.
    """

    @staticmethod
    def is_allowed(order: Order):
        """
        Determines whether the action can be performed on the given order.
        
        :param order: The order object.
        :return: bool indicating if the action is allowed.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @staticmethod
    def perform(order: Order):
        """
        Performs the action on the given order.
        
        :param order: The order object.
        :raises: TransitionNotAllowed if the action is not allowed.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class OrderActionRegistry:
    """
    A registry to map action names to their corresponding handler classes.
    This allows dynamic lookup and execution of actions based on their name.
    """
    _registry = {}

    @classmethod
    def register(cls, action_name: str, handler_class: type):
        """
        Registers an action handler class to a specific action name.
        
        :param action_name: The name of the action.
        :param handler_class: The handler class that implements the action.
        """
        cls._registry[action_name] = handler_class

    @classmethod
    def get_handler(cls, action_name: str):
        """
        Retrieves the handler class for the given action name.
        
        :param action_name: The name of the action.
        :return: The handler class for the specified action.
        :raises: KeyError if the action is not found in the registry.
        """
        try:
            return cls._registry[action_name]
        except KeyError:
            raise KeyError(f"No handler registered for action: {action_name}")

    @classmethod
    def perform_action(cls, order: Order, action_name: str, *args, **kwargs):
        """
        Performs the specified action on the order using the corresponding handler.
        
        :param order: The order object to perform the action on.
        :param action_name: The name of the action to perform.
        :raises: TransitionNotAllowed if the action is not allowed.
        """
        handler_class = cls.get_handler(action_name)
        handler = handler_class()

        if handler.is_allowed(order):
            return handler.perform(order, *args, **kwargs)
        else:
            raise TransitionNotAllowed(f"Action '{action_name}' not allowed.")