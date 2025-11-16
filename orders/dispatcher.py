"""
Dispatcher to find and execute registered order actions.
"""

from orders.registry.decorator import (
    get_registered_action, get_all_registered_actions
)


class OrderActionDispatcher:
    """
    Dispatch and execute registered order actions.
    """

    def __init__(self, order, actor):
        """
        Initialize the dispatcher with an order and an actor.
        Args:
            order (Order): The order instance to operate on.
            actor (User): The user performing the action.
        """
        self.order = order
        self.actor = actor

    @staticmethod
    def dispatch(action_name: str, order_id: int, actor=None, **params):
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
        action_class = get_registered_action(action_name)
        if not action_class:
            raise ValueError(f"Action '{action_name}' not found.")

        action_instance = action_class(order_id, actor=actor, **params)
        return action_instance.execute()

    @staticmethod
    def list_available_actions():
        """
        List all registered action names.

        Returns:
            list[str]: List of action names.
        """
        return list(get_all_registered_actions().keys())

    @staticmethod
    def get_action_class(action_name: str):
        """
        Retrieve the registered action class.

        Args:
            action_name (str): Registered action name.

        Returns:
            Type[BaseOrderAction] or None: The action class if found.
        """
        return get_registered_action(action_name)
    
    def run_action(self, action_class, **kwargs):
        """
        Run a specific action class with the current order and actor.
        Args:
            action_class (Type[BaseOrderAction]): The action class to execute.
            **kwargs: Additional parameters for the action.
        Returns:
            Any: Result of the action's execute() method.
        """
        action = action_class(order=self.order, actor=self.actor, **kwargs)
        result = action.execute()
        self._trigger_webhooks_if_needed(action)
        return result
    
    def _trigger_webhooks_if_needed(self, action):
        # Lazy import to avoid circular import issues
        from orders.webhooks.tasks import deliver_webhook_task
        
        writer = self.order.assigned_writer
        if not writer:
            return

        settings = getattr(writer, "webhook_settings", None)
        if not settings or not settings.enabled:
            return

        if action.event_name not in settings.subscribed_events:
            return

        deliver_webhook_task.delay(
            user_id=writer.id,
            platform=settings.platform,
            webhook_url=settings.webhook_url,
            event=action.event_name,
            order_id=self.order.id,
            triggered_by_id=self.actor.id,
            test=False,
            fallback_icon="https://yourcdn.com/images/default-avatar.png"
        )