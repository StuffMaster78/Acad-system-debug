from orders.registry.decorator import get_registered_action

def get_action_or_raise(name: str):
    """
    Retrieve a registered order action by name, raising an error if not found.
    Args:
        name (str): The name of the registered action.
    Returns:
    Type[BaseOrderAction]: The action class if found.
    Raises:
        ValueError: If the action is not registered.
    """
    action = get_registered_action(name)
    if not action:
        raise ValueError(f"Order action '{name}' not found in registry.")
    return action