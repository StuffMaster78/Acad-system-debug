from writer_compensation.exceptions.base import CompensationBaseException


class InvalidSettlementStateError(CompensationBaseException):
    """
    Settlement cannot proceed due to invalid state.
    """


class EmptySettlementError(CompensationBaseException):
    """
    No financial events found for settlement.
    """


class SettlementFinalizedError(CompensationBaseException):
    """
    Attempted mutation on locked settlement period.
    """