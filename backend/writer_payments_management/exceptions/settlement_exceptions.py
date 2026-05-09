from writer_payments_management.exceptions.base import PaymentsBaseException


class InvalidSettlementStateError(PaymentsBaseException):
    """
    Settlement cannot proceed due to invalid state.
    """


class EmptySettlementError(PaymentsBaseException):
    """
    No financial events found for settlement.
    """


class SettlementFinalizedError(PaymentsBaseException):
    """
    Attempted mutation on locked settlement period.
    """