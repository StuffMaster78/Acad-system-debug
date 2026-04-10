class PaymentError(Exception):
    """Base payment exception."""


class PaymentVerificationError(PaymentError):
    """Raised when verification fails."""


class DuplicatePaymentEventError(PaymentError):
    """Raised when duplicate webhook or transaction is detected."""


class PaymentIntentNotFoundError(PaymentError):
    """Raised when payment intent cannot be found."""


class InvalidPaymentStateError(PaymentError):
    """Raised when state transition is invalid."""


class RefundExecutionError(PaymentError):
    """Raised when refund execution fails."""