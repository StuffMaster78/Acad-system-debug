from writer_payments_management.exceptions.base import PaymentsBaseException


class LedgerSyncMismatchError(PaymentsBaseException):
    """
    Raised when wallet and ledger are out of sync.
    """


class LedgerDriftDetectedError(PaymentsBaseException):
    """
    Raised when exposure ledger drift is detected.
    """