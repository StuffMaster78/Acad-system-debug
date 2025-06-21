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


class OrderTransitionError(Exception):
    """Base class for order transition errors."""
    pass

class InvalidTransitionError(OrderTransitionError):
    """Raised when a transition is not allowed."""
    pass


class AlreadyInTargetStatusError(OrderTransitionError):
    """Raised when the order is already in the target status."""
    pass
class TransitionToPendingError(OrderTransitionError):
    """Raised when transitioning to pending fails."""
    pass
class TransitionToApprovedError(OrderTransitionError):
    """Raised when transitioning to approved fails."""
    pass
class TransitionToCancelledError(OrderTransitionError):
    """Raised when transitioning to cancelled fails."""
    pass
class TransitionToArchivedError(OrderTransitionError):
    """Raised when transitioning to archived fails."""
    pass
class TransitionToUnpaidError(OrderTransitionError):
    """Raised when transitioning to unpaid fails."""
    pass
class TransitionToPaidError(OrderTransitionError):
    """Raised when transitioning to paid fails."""
    pass
class TransitionToAvailableError(OrderTransitionError):
    """Raised when transitioning to available fails."""
    pass
class TransitionToInProgressError(OrderTransitionError):
    """Raised when transitioning to in_progress fails."""
    pass
class TransitionToOnHoldError(OrderTransitionError):
    """Raised when transitioning to on_hold fails."""
    pass
class TransitionToSubmittedError(OrderTransitionError):
    """Raised when transitioning to submitted fails."""
    pass
class TransitionToReviewedError(OrderTransitionError):
    """Raised when transitioning to reviewed fails."""
    pass
class TransitionToRatedError(OrderTransitionError):
    """Raised when transitioning to rated fails."""
    pass
class TransitionToRevisionRequestedError(OrderTransitionError):
    """Raised when transitioning to revision_requested fails."""
    pass
class TransitionToRevisionInProgressError(OrderTransitionError):
    """Raised when transitioning to revision_in_progress fails."""
    pass
class TransitionToRevisedError(OrderTransitionError):
    """Raised when transitioning to revised fails."""
    pass
class TransitionToReassignedError(OrderTransitionError):
    """Raised when transitioning to reassigned fails."""
    pass
class TransitionToCompleteError(OrderTransitionError):
    """Raised when transitioning to complete fails."""
    pass
class TransitionToCancelledByUserError(OrderTransitionError):
    """Raised when transitioning to cancelled by user fails."""
    pass
class TransitionToCancelledBySystemError(OrderTransitionError):
    """Raised when transitioning to cancelled by system fails."""
    pass
class TransitionToRevisionInProgressError(OrderTransitionError):
    """Raised when transitioning to revision_in_progress fails."""
    pass
class TransitionToRevisionRequestedError(OrderTransitionError):
    """Raised when transitioning to revision_requested fails."""
    pass
class TransitionToRevisionInProgressError(OrderTransitionError):
    """Raised when transitioning to revision_in_progress fails."""
    pass
class TransitionToRevisionRequestedError(OrderTransitionError):
    """Raised when transitioning to revision_requested fails."""
    pass
class TransitionToRevisionInProgressError(OrderTransitionError):
    """Raised when transitioning to revision_in_progress fails."""
    pass
class TransitionToRevisionRequestedError(OrderTransitionError):
    """Raised when transitioning to revision_requested fails."""
    pass
class TransitionToRevisionInProgressError(OrderTransitionError):
    """Raised when transitioning to revision_in_progress fails."""
    pass
class TransitionToRevisionRequestedError(OrderTransitionError):
    """Raised when transitioning to revision_requested fails."""
    pass

class IsClient(Exception):
    """Raised when an operation is attempted by a client user on an order."""
    pass
class IsWriter(Exception):
    """Raised when an operation is attempted by a writer user on an order."""
    pass
class OrderAlreadyExistsError(Exception):
    """Raised when an order with the same ID already exists."""
    pass

class IsSupportOrAdmin(Exception):
    """Raised when an operation is attempted by a user who is not a support or admin."""
    pass
class OrderAlreadyAssignedError(Exception):
    """Raised when an order is already assigned to a writer."""
    pass
class OrderNotFoundError(Exception):
    """Raised when an order cannot be found in the system."""
    pass
class OrderInvalidStateException(Exception):
    """Raised when an order is in an invalid state for the requested operation."""
    pass

class OrderTransitionError(Exception):
    """Raised when an invalid order transition is attempted."""
    pass

class AlreadyAssignedError(Exception):
    """Raised when an order is already assigned to a writer."""
    pass

class RequestNotFoundError(Exception):
    """Raised when a specific writer request cannot be found."""
    pass
