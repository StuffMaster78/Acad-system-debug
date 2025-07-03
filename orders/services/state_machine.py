# orders/services/state_machine.py (inside GenericStateMachineService)

from orders.models import OrderTransitionLog, Order

def transition_to(
        self, new_state: str, actor=None, action="manual",
        is_automatic=False, meta=None
    ) -> Order:
    """
    Transition the order to a new state, validating the transition and
    running any necessary hooks.
    Args:
        new_state (str): The desired new state for the order.
        actor (User, optional): The user performing the action. Defaults to None.
        action (str, optional): The action type (e.g., "manual", "automatic").
            Defaults to "manual".
        is_automatic (bool, optional): Whether the transition is automatic.
            Defaults to False.
        meta (dict, optional): Additional metadata for the transition.
            Defaults to None.
    Returns:
        Order: The updated order instance after the transition.
    Raises:
        ValueError: If the transition is not allowed or if the order
            is not in a valid state for the transition.
    """
    old_state = self.order.status

    # validate and execute transition...
    if not self.can_transition(new_state):
        raise ValueError(f"Cannot transition from {old_state} to {new_state}")

    # Run exit and enter hooks
    self._run_hook(f"on_exit_{old_state}")
    self.order.status = new_state
    self.order.save(update_fields=["status"])
    self._run_hook(f"on_enter_{new_state}")

    # Log the transition
    OrderTransitionLog.objects.create(
        order=self.order,
        user=actor if actor and actor.is_authenticated else None,
        old_status=old_state,
        new_status=new_state,
        action=action,
        is_automatic=is_automatic,
        meta=meta or {}
    )

    return self.order