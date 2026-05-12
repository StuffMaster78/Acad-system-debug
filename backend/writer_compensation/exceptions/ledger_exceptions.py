from writer_compensation.exceptions.base import CompensationBaseException


class LedgerSyncMismatchError(CompensationBaseException):
    """
    Raised when wallet and ledger are out of sync.
    """


class LedgerDriftDetectedError(CompensationBaseException):
    """
    Raised when exposure ledger drift is detected.
    """