class TransitionNotAllowed(Exception):
    """
    Raised when an order transition is not permitted
    due to its current state or business rules.
    """
    pass

class PolicyNotFound(Exception):
    """Raised when no active revision policy is found for a website."""
    pass

class InvalidOrderTransition(Exception):
    """
    Raised when an order cannot be transitioned to the desired status.
    """
    pass
