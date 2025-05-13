
from typing import Dict, Type
from orders.models import Order
from orders.exceptions import TransitionNotAllowed # type: ignore
from django.core.exceptions import ValidationError


class OrderActionHandler:
    """
    Base class for handling order actions.
    Each order action (e.g., transition, assign, complete) is a subclass of this.
    """

    @staticmethod
    def is_allowed(order: Order) -> bool:
        """
        Determines whether the action can be performed on the given order.

        :param order: The order object.
        :return: bool indicating if the action is allowed.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @staticmethod
    def perform(order: Order, *args, **kwargs):
        """
        Performs the action on the given order.

        :param order: The order object.
        :raises: TransitionNotAllowed if the action is not allowed.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def execute(self, order: Order, *args, **kwargs):
        """
        Entry point for all actions. Validates and performs the action.
        """
        if not self.is_allowed(order):
            raise TransitionNotAllowed("Action is not allowed for this order.")
        return self.perform(order, *args, **kwargs)


class OrderActionRegistry:
    """
    A registry to map action names to their corresponding handler classes.
    This allows dynamic lookup and execution of actions based on their name.
    """
    _registry: Dict[str, Type[OrderActionHandler]] = {}

    @classmethod
    def register(cls, name: str, handler_class: Type[OrderActionHandler]) -> None:
        """
        Registers an action handler class to a specific action name.

        :param name: The name of the action.
        :param handler_class: The handler class that implements the action.
        """
        if not issubclass(handler_class, OrderActionHandler):
            raise TypeError(f"{handler_class.__name__} must subclass OrderActionHandler")
        cls._registry[name] = handler_class

    @classmethod
    def get_handler(cls, name: str) -> Type[OrderActionHandler]:
        """
        Retrieves the handler class for the given action name.

        :param name: The name of the action.
        :return: The handler class for the specified action.
        :raises: KeyError if the action is not found in the registry.
        """
        try:
            return cls._registry[name]
        except KeyError:
            raise ValidationError(
                f"No order action registered under '{name}'"
            )

    @classmethod
    def all(cls) -> Dict[str, Type[OrderActionHandler]]:
        return cls._registry.copy()

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._registry.keys())

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