class CompensationError(Exception):
    """Base exception for all writer compensation errors."""
    pass


class NoOpenWindowError(CompensationError):
    """No open compensation window exists for this website."""
    pass


class WindowLockedError(CompensationError):
    """Window is locked (PROCESSING or DONE) and cannot accept new events."""
    pass


class InvalidWindowTransitionError(CompensationError):
    """Attempted an invalid window status transition."""
    pass


class InvalidPayoutItemTransitionError(CompensationError):
    """Attempted an invalid PayoutItem status transition."""
    pass


class DuplicateEventError(CompensationError):
    """An event with this idempotency key already exists."""
    pass


class ZeroAmountError(CompensationError):
    """Compensation event amount cannot be zero."""
    pass


class WindowOverlapError(CompensationError):
    """A compensation window already exists covering this date range."""
    pass


class CycleChangeNotAllowedError(CompensationError):
    """Writer already has a pending cycle change request."""
    pass


class PayoutItemNotFoundError(CompensationError):
    """PayoutItem does not exist for this writer in this batch."""
    pass