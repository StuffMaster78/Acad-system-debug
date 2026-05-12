from writer_compensation.exceptions.base import CompensationBaseException


class PayoutFailedError(CompensationBaseException):
    """
    External payout failed.
    """


class PayoutBatchError(CompensationBaseException):
    """
    Payout batch creation or processing error.
    """