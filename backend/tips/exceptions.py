class TipError(Exception):
    """
    Base exception for tip domain.
    """


class TipValidationError(TipError):
    """
    Raised when tip input violates business rules.
    """


class TipIdempotencyError(TipError):
    """
    Raised when idempotency rules are violated.
    """


class TipPolicyError(TipError):
    """
    Raised when policy resolution fails or is invalid.
    """


class TipSettlementError(TipError):
    """
    Raised when settlement cannot be completed.
    """