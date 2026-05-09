from writer_payments_management.exceptions.base import PaymentsBaseException


class PayoutFailedError(PaymentsBaseException):
    """
    External payout failed.
    """


class PayoutBatchError(PaymentsBaseException):
    """
    Payout batch creation or processing error.
    """