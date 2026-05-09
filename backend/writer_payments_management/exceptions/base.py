class PaymentsBaseException(Exception):
    """
    Root exception for all payment domain errors.
    """


class ValidationError(PaymentsBaseException):
    """
    Raised when a business rule is violated.
    """


class InsufficientBalanceError(PaymentsBaseException):
    """
    Raised when wallet or ledger cannot cover an operation.
    """


class SettlementError(PaymentsBaseException):
    """
    Raised when settlement processing fails.
    """


class ExposureError(PaymentsBaseException):
    """
    Raised when exposure limits are breached.
    """


class ReconciliationError(PaymentsBaseException):
    """
    Raised when ledger vs wallet vs payout mismatches occur.
    """