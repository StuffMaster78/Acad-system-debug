class CompensationBaseException(Exception):
    """
    Root exception for all writer compensation domain errors.
    """


PaymentsBaseException = CompensationBaseException


class ValidationError(CompensationBaseException):
    """
    Raised when a business rule is violated.
    """


class InsufficientBalanceError(CompensationBaseException):
    """
    Raised when wallet or ledger cannot cover an operation.
    """


class SettlementError(CompensationBaseException):
    """
    Raised when settlement processing fails.
    """


class ExposureError(CompensationBaseException):
    """
    Raised when exposure limits are breached.
    """


class ReconciliationError(CompensationBaseException):
    """
    Raised when ledger vs wallet vs payout mismatches occur.
    """
