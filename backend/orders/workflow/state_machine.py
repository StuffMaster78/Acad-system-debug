from typing import Any, Dict, List


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""


class GenericStateMachineService:
    """
    A generic finite state machine for managing status transitions.

    Attributes:
        transition_map (dict): A dictionary mapping current states to
            lists of allowed next states.
    """

    def __init__(self, transition_map: Dict[str, List[str]]):
        """
        Initializes the state machine with a transition map.

        Args:
            transition_map (Dict[str, List[str]]): A dictionary where keys
                are current states and values are lists of valid next states.
        """
        self.transition_map = transition_map

    def can_transition(self, current: str, new: str) -> bool:
        """
        Checks if a transition is allowed from current to new state.

        Args:
            current (str): The current state.
            new (str): The desired new state.

        Returns:
            bool: True if the transition is valid, False otherwise.
        """
        return new in self.transition_map.get(current, [])

    def transition(self, instance: Any, to_status: str, attr: str = "status"):
        """
        Transitions an instance to a new state if valid.

        Args:
            instance (Any): The object to transition (e.g. an Order).
            to_status (str): The desired new status.
            attr (str): The name of the status attribute on the instance.

        Returns:
            Any: The updated instance after saving.

        Raises:
            InvalidTransitionError: If the transition is not allowed.
        """
        current_status = getattr(instance, attr)
        if not self.can_transition(current_status, to_status):
            raise InvalidTransitionError(
                f"Cannot transition from {current_status} to {to_status}."
            )
        setattr(instance, attr, to_status)
        instance.save(update_fields=[attr])
        return instance
